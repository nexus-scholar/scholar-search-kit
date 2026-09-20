"""Abstract backfilling for documents with missing abstracts."""

from __future__ import annotations

import logging
from typing import Any

from .http_client import AcademicHttpClient
from .models import Document

logger = logging.getLogger(__name__)


class AbstractHydrator:
    """Batch-queries Semantic Scholar and OpenAlex for missing abstracts."""

    S2_BASE = "https://api.semanticscholar.org/graph/v1"
    OA_BASE = "https://api.openalex.org"

    def __init__(self, http_client: AcademicHttpClient):
        self.http_client = http_client

    async def hydrate_missing_abstracts(
        self, documents: list[Document], batch_size: int = 50
    ) -> tuple[list[Document], dict[str, int]]:
        """Hydrate documents with missing abstracts from S2 and OpenAlex.

        Args:
            documents: List of documents to hydrate.
            batch_size: Number of DOIs to query per batch.

        Returns:
            Tuple of (hydrated documents, stats dict).
        """
        stats = {"attempted": 0, "hydrated": 0, "failed": 0}

        # Filter docs needing abstracts
        needs_abstract = [
            doc for doc in documents if not doc.abstract and doc.external_ids.doi
        ]

        stats["attempted"] = len(needs_abstract)

        if not needs_abstract:
            return documents, stats

        # Process in batches
        hydrated_map: dict[str, str] = {}

        for i in range(0, len(needs_abstract), batch_size):
            batch = needs_abstract[i : i + batch_size]
            dois = [doc.external_ids.doi for doc in batch if doc.external_ids.doi]

            # Try S2 first
            s2_results = await self._hydrate_from_s2(dois)
            hydrated_map.update(s2_results)

            # Fallback to OpenAlex for missing
            missing_dois = [d for d in dois if d not in hydrated_map]
            if missing_dois:
                oa_results = await self._hydrate_from_openalex(missing_dois)
                hydrated_map.update(oa_results)

        # Apply hydrated abstracts
        for doc in documents:
            if doc.external_ids.doi and doc.external_ids.doi in hydrated_map:
                doc.abstract = hydrated_map[doc.external_ids.doi]
                stats["hydrated"] += 1
            elif doc.external_ids.doi and not doc.abstract:
                stats["failed"] += 1

        return documents, stats

    async def _hydrate_from_s2(self, dois: list[str]) -> dict[str, str]:
        """Batch-query Semantic Scholar for abstracts."""
        if not dois:
            return {}

        try:
            url = f"{self.S2_BASE}/paper/batch"
            payload = {"ids": [f"DOI:{doi}" for doi in dois]}
            params = {"fields": "paperId,externalIds,abstract"}

            response = await self.http_client.post(url, json=payload, params=params)

            if response.status_code != 200:
                logger.warning(f"S2 batch request failed: {response.status_code}")
                return {}

            results = response.json()
            abstract_map = {}

            for item in results:
                if item and item.get("abstract"):
                    ext_ids = item.get("externalIds", {})
                    doi = ext_ids.get("DOI")
                    if doi:
                        abstract_map[doi] = item["abstract"]

            return abstract_map
        except Exception as e:
            logger.warning(f"S2 hydration failed: {e}")
            return {}

    async def _hydrate_from_openalex(self, dois: list[str]) -> dict[str, str]:
        """Query OpenAlex for abstracts using inverted index."""
        if not dois:
            return {}

        abstract_map = {}

        for doi in dois:
            try:
                # Use filter parameter for reliable DOI matching
                url = f"{self.OA_BASE}/works?filter=doi:{doi}"
                response = await self.http_client.get(url)

                if response.status_code != 200:
                    continue

                data = response.json()
                # OpenAlex returns a list of works
                works = data.get("results", [])
                if not works:
                    continue

                work = works[0]
                inverted_index = work.get("abstract_inverted_index")

                if inverted_index:
                    abstract = self._reconstruct_abstract(inverted_index)
                    if abstract:
                        abstract_map[doi] = abstract
            except Exception as e:
                logger.debug(f"OpenAlex lookup failed for {doi}: {e}")
                continue

        return abstract_map

    @staticmethod
    def _reconstruct_abstract(inverted_index: dict[str, list[int]]) -> str:
        """Reconstruct abstract from OpenAlex inverted index."""
        if not inverted_index:
            return ""

        word_positions = []
        for word, positions in inverted_index.items():
            for pos in positions:
                word_positions.append((pos, word))

        word_positions.sort(key=lambda x: x[0])
        return " ".join(w for _, w in word_positions)
