"""arXiv provider implementation."""

import xml.etree.ElementTree as ET
from collections.abc import AsyncIterator

from ..models import Author, Document, ExternalIds, Query
from ..query_translator import BooleanQueryTranslator, QueryField
from .base import BaseAPIProvider


class ArxivProvider(BaseAPIProvider):
    """Searches arXiv API (http://export.arxiv.org/api/query)."""

    def __init__(self) -> None:
        # arXiv allows 1 req/sec without API key
        super().__init__(name="arxiv", rate_limit=1.0)
        self.base_url = "http://export.arxiv.org/api/query"
        self.ns = {"atom": "http://www.w3.org/2005/Atom"}

        # arXiv supports AND, OR, ANDNOT. Prefixes: all, ti, au, abs
        self.translator = BooleanQueryTranslator(
            field_map={
                QueryField.ANY: "all",
                QueryField.TITLE: "ti",
                QueryField.ABSTRACT: "abs",
                QueryField.AUTHOR: "au",
            },
            operator_map={"AND": "AND", "OR": "OR", "NOT": "ANDNOT"},
        )

    def _parse_xml_entry(
        self, entry: ET.Element, query_id: str | None = None
    ) -> Document:
        """Converts an arXiv Atom XML entry into a Document model."""

        # Parse Title
        title_elem = entry.find("atom:title", self.ns)
        title = (
            title_elem.text.strip().replace("\n", " ")
            if title_elem is not None
            else "Untitled"
        )

        # Parse Abstract
        summary_elem = entry.find("atom:summary", self.ns)
        abstract = (
            summary_elem.text.strip().replace("\n", " ")
            if summary_elem is not None
            else None
        )

        # Parse Year (from published date)
        year = None
        published_elem = entry.find("atom:published", self.ns)
        if published_elem is not None and published_elem.text:
            year = int(published_elem.text[:4])

        # Parse Authors
        authors = []
        for author_elem in entry.findall("atom:author", self.ns):
            name_elem = author_elem.find("atom:name", self.ns)
            if name_elem is not None and name_elem.text:
                name_parts = name_elem.text.strip().split(" ")
                if len(name_parts) > 1:
                    authors.append(
                        Author(
                            given_name=" ".join(name_parts[:-1]),
                            family_name=name_parts[-1],
                        )
                    )
                else:
                    authors.append(Author(family_name=name_parts[0]))

        # Extract Arxiv ID from the ID URL (e.g. http://arxiv.org/abs/2101.01234v1 -> 2101.01234)
        id_elem = entry.find("atom:id", self.ns)
        arxiv_id = None
        if id_elem is not None and id_elem.text:
            arxiv_id = id_elem.text.split("/")[-1].split("v")[
                0
            ]  # Remove version number

        # Extract DOI if available (often added after peer review publication)
        doi = None
        for link_elem in entry.findall("atom:link", self.ns):
            title_attr = link_elem.get("title")
            if title_attr == "doi":
                doi_url = link_elem.get("href", "")
                if "doi.org/" in doi_url:
                    doi = doi_url.split("doi.org/")[-1]

        # PDF URL
        pdf_url = None
        for link_elem in entry.findall("atom:link", self.ns):
            if link_elem.get("title") == "pdf":
                pdf_url = link_elem.get("href")

        external_ids = ExternalIds(doi=doi, arxiv_id=arxiv_id)

        doc = Document(
            title=title,
            year=year,
            provider=self.name,
            provider_id=arxiv_id or "",
            external_ids=external_ids,
            abstract=abstract,
            authors=authors,
            venue="arXiv Preprint",
            url=pdf_url or (id_elem.text if id_elem is not None else None),
            query_id=query_id,
        )
        doc.mark_retrieved()
        return doc

    async def search(self, query: Query) -> AsyncIterator[Document]:
        """Search arXiv."""
        translated_query = self.translator.translate(query)

        # If translator didn't apply any field, fallback to all:
        if ":" not in translated_query:
            translated_query = f'all:"{translated_query}"'

        params = {
            "search_query": translated_query,
            "start": 0,
            "max_results": min(query.max_results or 100, 1000),
        }

        # arXiv doesn't support direct year filtering in the query string well,
        # so we fetch and filter locally.

        response = await self.client.get(self.base_url, params=params)

        # Parse XML
        if not response.text.strip():
            return
            
        root = ET.fromstring(response.content)
        count = 0

        for entry in root.findall("atom:entry", self.ns):
            doc = self._parse_xml_entry(entry, query.id)

            if query.year_min and (doc.year or 0) < query.year_min:
                continue
            if query.year_max and (doc.year or 9999) > query.year_max:
                continue

            yield doc
            count += 1
            if query.max_results and count >= query.max_results:
                return

    # arXiv has no native snowballing API
