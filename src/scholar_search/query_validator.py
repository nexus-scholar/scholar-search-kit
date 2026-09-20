"""Query validation and healing for golden seed recall."""

from __future__ import annotations

import re
from typing import Any

from .models import Query


def _clean_doi(doi: str) -> str:
    """Sanitize DOI by removing common prefixes."""
    doi = doi.strip()
    doi = re.sub(r"^https?://doi\.org/", "", doi)
    doi = re.sub(r"^doi:", "", doi, flags=re.IGNORECASE)
    doi = doi.strip("/")
    return doi


class QueryDiagnosticValidator:
    """Validates search queries against golden seed DOIs and heals if needed."""

    def __init__(self, search_engine: Any, max_iterations: int = 3):
        self.search_engine = search_engine
        self.max_iterations = max_iterations

    async def validate_and_heal(
        self,
        query_text: str,
        golden_seeds: list[str],
        providers: list[str] | None = None,
    ) -> dict:
        """Validate query recall against golden seeds, heal if needed."""
        if not golden_seeds:
            return {
                "original_query": query_text,
                "golden_seeds": [],
                "iterations": [],
                "final_query": query_text,
                "recall": 1.0,
                "validated": True,
            }

        seeds_lower = {_clean_doi(s).lower() for s in golden_seeds}
        current_query = query_text
        iterations = []

        for i in range(self.max_iterations):
            query_obj = Query(text=current_query)
            results = await self.search_engine.search_all(query_obj, dedup=True)
            found_dois = {
                _clean_doi(r.external_ids.doi).lower()
                for r in results
                if r.external_ids.doi
            }
            found_seeds = seeds_lower & found_dois
            missed_seeds = seeds_lower - found_seeds
            recall = len(found_seeds) / len(seeds_lower) if seeds_lower else 1.0

            iterations.append(
                {
                    "iteration": i + 1,
                    "query": current_query,
                    "results_count": len(results),
                    "recall": recall,
                    "found_seeds": list(found_seeds),
                    "missed_seeds": list(missed_seeds),
                }
            )

            if recall >= 1.0:
                return {
                    "original_query": query_text,
                    "golden_seeds": golden_seeds,
                    "iterations": iterations,
                    "final_query": current_query,
                    "recall": recall,
                    "validated": True,
                }

            if i < self.max_iterations - 1:
                current_query = await self._heal_query(
                    current_query, missed_seeds, results
                )

        return {
            "original_query": query_text,
            "golden_seeds": golden_seeds,
            "iterations": iterations,
            "final_query": current_query,
            "recall": iterations[-1]["recall"] if iterations else 0.0,
            "validated": False,
        }

    async def _heal_query(
        self,
        current_query: str,
        missed_seeds: set[str],
        search_results: list,
    ) -> str:
        """Heal query by appending DOI-based OR clause."""
        if not missed_seeds:
            return current_query

        doi_terms = " OR ".join(f"doi:{doi}" for doi in missed_seeds)
        healed = f"({current_query}) OR ({doi_terms})"
        return healed
