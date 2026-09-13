"""OpenAlex provider implementation."""

import re
from collections.abc import AsyncIterator
from typing import Any

from ..config import settings
from ..models import Author, Document, ExternalIds, Query
from ..query_translator import BooleanQueryTranslator, QueryField
from .base import BaseAPIProvider


class OpenAlexProvider(BaseAPIProvider):
    """Searches the OpenAlex API (https://api.openalex.org/works)."""

    def __init__(self) -> None:
        super().__init__(name="openalex", rate_limit=settings.rate_limit_openalex)
        self.base_url = "https://api.openalex.org/works"

        # OpenAlex doesn't have native advanced boolean search, but it supports phrase search
        # We'll use a simple translator mapping to generic text search
        self.translator = BooleanQueryTranslator(
            field_map={
                QueryField.ANY: "",
                QueryField.TITLE: "title.search",
                QueryField.ABSTRACT: "abstract.search",
            },
            operator_map={"AND": " ", "OR": " ", "NOT": "-"},  # Basic approximations
        )

    def _normalize_document(
        self, raw: dict[str, Any], query_id: str | None = None
    ) -> Document:
        """Converts OpenAlex JSON into a Document model."""

        # Parse authors
        authors = []
        for authorship in raw.get("authorships", []):
            author_data = authorship.get("author", {})
            name_parts = author_data.get("display_name", "").split(" ")

            if len(name_parts) > 1:
                authors.append(
                    Author(
                        given_name=" ".join(name_parts[:-1]),
                        family_name=name_parts[-1],
                        orcid=author_data.get("orcid"),
                    )
                )
            elif name_parts and name_parts[0]:
                authors.append(
                    Author(family_name=name_parts[0], orcid=author_data.get("orcid"))
                )

        # Parse External IDs
        ids = raw.get("ids", {})
        external_ids = ExternalIds(
            doi=ids.get("doi"),
            pubmed_id=ids.get("pmid"),
            openalex_id=ids.get("openalex"),
        )

        # Best Open Access URL
        oa_url = None
        best_oa = raw.get("best_oa_location")
        if best_oa:
            oa_url = best_oa.get("pdf_url") or best_oa.get("landing_page_url")

        location = raw.get("primary_location") or {}
        source = location.get("source") or {}
        venue_name = source.get("display_name")

        doc = Document(
            title=raw.get("title") or "Untitled",
            year=raw.get("publication_year"),
            provider=self.name,
            provider_id=raw.get("id", ""),
            external_ids=external_ids,
            abstract=self._parse_abstract_inverted_index(
                raw.get("abstract_inverted_index")
            ),
            authors=authors,
            venue=venue_name,
            url=oa_url or raw.get("id"),
            citations_count=raw.get("cited_by_count", 0),
            references_count=len(raw.get("referenced_works", [])),
            topics=self._extract_topics(raw),
            query_id=query_id,
        )
        doc.mark_retrieved()
        return doc

    def _extract_topics(self, raw: dict[str, Any]) -> list[dict[str, Any]] | None:
        """Classifier-grounded taxonomy from OpenAlex ``topics`` (else deprecated ``concepts``).

        Each entry is normalized to ``{"source", "id", "display_name", "score"}``
        (``score`` is ``None`` when the record carries no score).  Returns
        ``None`` when neither list is populated (e.g. non-OpenAlex inputs).
        """
        topics = raw.get("topics")
        if isinstance(topics, list) and topics:
            return self._topic_entries(topics, "openalex_topics")
        concepts = raw.get("concepts")
        if isinstance(concepts, list) and concepts:
            return self._topic_entries(concepts, "openalex_concepts")
        return None

    def _topic_entries(
        self, entries: list[Any], source: str
    ) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            normalized.append(
                {
                    "source": source,
                    "id": entry.get("id"),
                    "display_name": entry.get("display_name"),
                    "score": entry.get("score"),
                }
            )
        return normalized

    def _parse_abstract_inverted_index(
        self, inverted_index: dict[str, list[int]] | None
    ) -> str | None:
        """OpenAlex returns abstracts as inverted indexes to save bandwidth. We must reconstruct it."""
        if not inverted_index:
            return None

        word_index = []
        for word, positions in inverted_index.items():
            for pos in positions:
                word_index.append((pos, word))

        word_index.sort(key=lambda x: x[0])
        return " ".join(word for _, word in word_index)

    def _build_params(self, query: Query) -> dict[str, Any]:
        params: dict[str, Any] = {
            "mailto": settings.mailto,
        }
        if query.semantic:
            # Semantic mode (M0.6): OpenAlex rejects cursor pagination for
            # `search.semantic` (page/per_page only, max 50 results per
            # request), so cap per-page and never set a cursor key.
            params["per-page"] = min(query.max_results or 50, 50)
        else:
            params["per-page"] = min(query.max_results or 100, 200)
            params["cursor"] = "*"
        if settings.openalex_key:
            params["api_key"] = settings.openalex_key

        filters: list[str] = []
        if query.year_min:
            filters.append(f"from_publication_date:{query.year_min}-01-01")
        if query.year_max:
            filters.append(f"to_publication_date:{query.year_max}-12-31")

        query_text = (query.text or "").strip()
        if query.semantic:
            # Semantic mode (M0.6): raw meaning-matched text, no boolean
            # rewriting, and never combined with the keyword `search=` param.
            params["search.semantic"] = query_text
        elif " AND " in query_text:
            clauses = re.split(r"\s+AND\s+", query_text, flags=re.IGNORECASE)
            selected_terms = []
            for c in clauses:
                phrases = re.findall(r'"([^"]+)"', c)
                if phrases:
                    selected_terms.append(f'"{phrases[0]}"')
                else:
                    words = [
                        w
                        for w in re.findall(r"\b[a-zA-Z0-9_-]{3,}\b", c)
                        if w.upper() not in ("OR", "NOT", "AND")
                    ]
                    if words:
                        selected_terms.append(words[0])
            params["search"] = " ".join(selected_terms) if selected_terms else query_text
        elif " OR " in query_text:
            phrases = re.findall(r'"([^"]+)"', query_text)
            if phrases:
                params["search"] = f'"{phrases[0]}"'
            else:
                words = [
                    w
                    for w in re.findall(r"\b[a-zA-Z0-9_-]{3,}\b", query_text)
                    if w.upper() not in ("OR", "NOT", "AND")
                ]
                params["search"] = words[0] if words else query_text
        elif query_text:
            params["search"] = query_text

        if filters and not query.semantic:
            # Semantic mode: OpenAlex `search.semantic` rejects a `filter`
            # param (HTTP 400, verified live 2026-09-13). The ``search`` loop
            # performs manual year filtering for semantic mode instead.
            params["filter"] = ",".join(filters)

        return params

    async def search(self, query: Query) -> AsyncIterator[Document]:
        """Search OpenAlex works."""
        params = self._build_params(query)

        count = 0
        page = 1
        while True:
            resp = await self.client.get(self.base_url, params=params)
            response = resp.json()

            for item in response.get("results", []):
                # Manual year filtering (if filter logic gets too complex for query params)
                pub_year = item.get("publication_year")
                if pub_year:
                    if query.year_min and pub_year < query.year_min:
                        continue
                    if query.year_max and pub_year > query.year_max:
                        continue

                yield self._normalize_document(item, query.id)
                count += 1
                if query.max_results and count >= query.max_results:
                    return

            if query.semantic:
                # Semantic mode (M0.6): page-based pagination only.  OpenAlex
                # caps `search.semantic` at 50 results / request and rejects
                # cursor pagination, so walk pages via ``page`` counter.
                total = response.get("meta", {}).get("count")
                if not response.get("results"):
                    break
                if query.max_results and count >= query.max_results:
                    break
                if total is not None and count >= total:
                    break
                page += 1
                params["page"] = page
            else:
                cursor = response.get("meta", {}).get("next_cursor")
                if not cursor:
                    break
                params["cursor"] = cursor

    async def get_citations(self, document_id: str) -> AsyncIterator[Document]:
        """Forward Snowballing: Get papers that cite this specific OpenAlex ID."""
        # e.g., filter=cites:W123456789
        params = {"filter": f"cites:{document_id}", "per-page": 200, "cursor": "*"}
        if settings.openalex_key:
            params["api_key"] = settings.openalex_key

        while True:
            resp = await self.client.get(self.base_url, params=params)
            response = resp.json()
            for item in response.get("results", []):
                yield self._normalize_document(item)

            cursor = response.get("meta", {}).get("next_cursor")
            if not cursor:
                break
            params["cursor"] = cursor

    async def get_references(self, document_id: str) -> AsyncIterator[Document]:
        """Backward Snowballing: Get papers that this specific OpenAlex ID cites."""
        # Fetch the document first
        doc_resp = await self.client.get(f"{self.base_url}/{document_id}")
        doc_response = doc_resp.json()
        referenced_works = doc_response.get("referenced_works", [])

        if not referenced_works:
            return

        # OpenAlex allows filtering by a list of IDs (max 50 per request usually, but we'll use a chunked approach)
        chunk_size = 50
        for i in range(0, len(referenced_works), chunk_size):
            chunk = referenced_works[i : i + chunk_size]
            id_filter = "|".join(chunk)

            params = {"filter": f"openalex:{id_filter}", "per-page": 200}
            if settings.openalex_key:
                params["api_key"] = settings.openalex_key

            resp = await self.client.get(self.base_url, params=params)
            response = resp.json()
            for item in response.get("results", []):
                yield self._normalize_document(item)
