"""OpenAlex provider implementation."""

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
            query_id=query_id,
        )
        doc.mark_retrieved()
        return doc

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

    async def search(self, query: Query) -> AsyncIterator[Document]:
        """Search OpenAlex works."""

        translated_query = self.translator.translate(query)

        params = {
            "search": translated_query,
            "per-page": min(query.max_results or 100, 200),
            "cursor": "*",
            "mailto": settings.mailto,
        }

        if settings.openalex_key:
            params["api_key"] = settings.openalex_key

        count = 0
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
