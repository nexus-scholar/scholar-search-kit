"""Protocol adapter for scholar-search-kit to consume Phase 0 ResearchProtocols."""

import json
from pathlib import Path
from typing import Any

from .models import Query


def compile_protocol_search(
    protocol_input: dict[str, Any] | str | Path,
) -> tuple[Query, list[str]]:
    """
    Compiles a Phase 0 protocol.json into a federated Query object and a list of target database providers.

    Returns:
        tuple[Query, list[str]]: (Compiled Query, List of provider names)
    """
    if isinstance(protocol_input, (str, Path)):
        path = Path(protocol_input)
        if not path.exists():
            raise FileNotFoundError(f"Protocol file not found at: {path}")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    elif isinstance(protocol_input, dict):
        data = protocol_input
    else:
        # Pydantic model (e.g. ResearchProtocol)
        if hasattr(protocol_input, "model_dump"):
            data = protocol_input.model_dump()
        else:
            raise TypeError(f"Unsupported protocol input type: {type(protocol_input)}")

    search_strategy = data.get("search_strategy", {})
    core_concepts = search_strategy.get("core_concepts", [])

    concept_clauses: list[str] = []
    for concept_item in core_concepts:
        concept_name = concept_item.get("concept", "").strip()
        synonyms = concept_item.get("synonyms", [])
        operator = concept_item.get("boolean_operator", "OR").upper()

        terms = [concept_name] + [s.strip() for s in synonyms if s.strip()]
        # Quote multi-word terms
        quoted_terms = [
            f'"{t}"' if " " in t and not (t.startswith('"') and t.endswith('"')) else t
            for t in terms
            if t
        ]

        if not quoted_terms:
            continue

        if len(quoted_terms) == 1:
            concept_clauses.append(quoted_terms[0])
        else:
            concept_clauses.append(f"({f' {operator} '.join(quoted_terms)})")

    if not concept_clauses:
        # Fallback to project title if no concepts specified
        title = data.get("metadata", {}).get("title", "")
        query_text = f'"{title}"' if title else "research"
    else:
        query_text = " AND ".join(concept_clauses)

    date_range = search_strategy.get("date_range") or {}
    year_min = date_range.get("start_year")
    year_max = date_range.get("end_year")

    languages = search_strategy.get("languages", ["en"])
    primary_lang = languages[0] if languages else "en"

    pool_size = search_strategy.get("target_candidate_pool_size") or {}
    max_results = pool_size.get("max", 100)

    target_databases = search_strategy.get(
        "target_databases",
        ["openalex", "semanticscholar", "crossref", "arxiv"],
    )

    query = Query(
        text=query_text,
        id=data.get("protocol_id", "Q001"),
        year_min=year_min,
        year_max=year_max,
        language=primary_lang,
        max_results=max_results,
    )

    return query, target_databases
