"""bioRxiv provider implementation."""

from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any

from ..models import Author, Document, ExternalIds, Query
from ..query_translator import BooleanQueryTranslator, QueryField
from .base import BaseAPIProvider


class BiorxivProvider(BaseAPIProvider):
    """Searches bioRxiv API (https://api.biorxiv.org).

    Note: bioRxiv API is chronological, not keyword-based.
    This provider fetches by date range and applies keyword filtering locally.
    """

    def __init__(self) -> None:
        super().__init__(name="biorxiv", rate_limit=1.0)
        self.base_url = "https://api.biorxiv.org/details/biorxiv"

        # BioRxiv uses local filtering, so we'll just clean the text
        self.translator = BooleanQueryTranslator(
            field_map={QueryField.ANY: ""},
            operator_map={"AND": "", "OR": "", "NOT": ""},
        )

    def _normalize_document(
        self, raw: dict[str, Any], query_id: str | None = None
    ) -> Document:
        """Converts bioRxiv JSON into a Document model."""

        # Parse Authors
        authors = []
        author_string = raw.get("authors", "")
        if author_string:
            # bioRxiv returns semi-colon separated authors
            for auth in author_string.split(";"):
                parts = auth.strip().split(" ")
                if len(parts) > 1:
                    authors.append(
                        Author(given_name=" ".join(parts[:-1]), family_name=parts[-1])
                    )
                elif parts and parts[0]:
                    authors.append(Author(family_name=parts[0]))

        # Parse Year
        year = None
        date_str = raw.get("date")
        if date_str:
            try:
                year = int(date_str[:4])
            except ValueError:
                pass

        # Parse IDs
        doi = raw.get("doi")

        doc = Document(
            title=raw.get("title") or "Untitled",
            year=year,
            provider=self.name,
            provider_id=doi or "",
            external_ids=ExternalIds(doi=doi),
            abstract=raw.get("abstract"),
            authors=authors,
            venue=raw.get("server"),  # usually "biorxiv"
            url=f"https://www.biorxiv.org/content/{doi}" if doi else None,
            query_id=query_id,
        )
        doc.mark_retrieved()
        return doc

    async def search(self, query: Query) -> AsyncIterator[Document]:
        """Search bioRxiv works chronologically and filter locally."""

        translated_query = self.translator.translate(query)
        terms = [
            term.lower()
            for term in translated_query.split()
            if term and term not in ["and", "or", "not"]
        ]

        # Setup date range
        start_year = query.year_min or 2013  # bioRxiv launched in 2013
        end_year = query.year_max or datetime.now().year

        start_date = f"{start_year}-01-01"
        end_date = f"{end_year}-12-31"

        cursor = 0
        count = 0

        while True:
            # Endpoint format: /details/server/start_date/end_date/cursor
            url = f"{self.base_url}/{start_date}/{end_date}/{cursor}"
            resp = await self.client.get(url)
            response = resp.json()

            messages = response.get("messages", [])
            if not messages:
                break

            status = messages[0].get("status")
            if status != "ok":
                break

            collection = response.get("collection", [])
            if not collection:
                break

            for item in collection:
                doc = self._normalize_document(item, query.id)

                # Local keyword filtering
                haystack = f"{doc.title} {doc.abstract or ''}".lower()
                if terms and not all(term in haystack for term in terms):
                    continue

                yield doc
                count += 1
                if query.max_results and count >= query.max_results:
                    return

            cursor += len(collection)

    # Snowballing not supported natively by bioRxiv API
