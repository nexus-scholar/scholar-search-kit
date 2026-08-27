"""PubMed provider implementation."""

import xml.etree.ElementTree as ET
from collections.abc import AsyncIterator

from ..config import settings
from ..models import Author, Document, ExternalIds, Query
from ..query_translator import BooleanQueryTranslator, QueryField
from .base import BaseAPIProvider


class PubMedProvider(BaseAPIProvider):
    """Searches PubMed via NCBI E-utilities."""

    def __init__(self) -> None:
        super().__init__(name="pubmed", rate_limit=settings.rate_limit_pubmed)
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

        # PubMed naturally supports AND, OR, NOT and fields via [Tag]
        self.translator = BooleanQueryTranslator(
            field_map={
                QueryField.ANY: "",
                QueryField.TITLE: "ti",
                QueryField.ABSTRACT: "ab",
                QueryField.AUTHOR: "au",
            },
            operator_map={"AND": "AND", "OR": "OR", "NOT": "NOT"},
        )

    async def _fetch_details(
        self, pmids: list[str], query_id: str | None = None
    ) -> AsyncIterator[Document]:
        """Fetches full XML details for a list of PMIDs and yields Document models."""
        if not pmids:
            return

        params = {"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"}

        resp = await self.client.get(f"{self.base_url}/efetch.fcgi", params=params)
        root = ET.fromstring(resp.content)

        for article_elem in root.findall(".//PubmedArticle"):
            medline = article_elem.find("MedlineCitation")
            article = medline.find("Article") if medline is not None else None

            if medline is None or article is None:
                continue

            # Parse IDs
            pmid = medline.findtext("PMID")
            doi = None
            pmcid = None
            for id_elem in article_elem.findall(".//ArticleId"):
                id_type = id_elem.get("IdType")
                if id_type == "doi":
                    doi = id_elem.text
                elif id_type == "pmc":
                    pmcid = id_elem.text

            # Parse Year
            year = None
            pub_date = article.find(".//PubDate")
            if pub_date is not None:
                year_elem = pub_date.find("Year")
                if year_elem is not None and year_elem.text:
                    try:
                        year = int(year_elem.text)
                    except ValueError:
                        pass

            # Parse Authors
            authors = []
            for author_elem in article.findall(".//Author"):
                last = author_elem.findtext("LastName")
                first = author_elem.findtext("ForeName") or author_elem.findtext(
                    "Initials"
                )
                if last:
                    authors.append(Author(family_name=last, given_name=first))

            # Parse MeSH Terms
            mesh_terms = []
            for mesh_elem in medline.findall(".//MeshHeading/DescriptorName"):
                if mesh_elem.text:
                    mesh_terms.append(mesh_elem.text)

            # Title & Abstract
            title = article.findtext("ArticleTitle", default="Untitled")

            abstract = None
            abstract_elem = article.find("Abstract")
            if abstract_elem is not None:
                abstract_texts = []
                for text_elem in abstract_elem.findall("AbstractText"):
                    if text_elem.text:
                        abstract_texts.append(text_elem.text)
                abstract = " ".join(abstract_texts) if abstract_texts else None

            doc = Document(
                title=title,
                year=year,
                provider=self.name,
                provider_id=pmid or "",
                external_ids=ExternalIds(doi=doi, pubmed_id=pmid),
                abstract=abstract,
                authors=authors,
                venue=article.findtext(".//Journal/Title"),
                url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else None,
                mesh_terms=mesh_terms,
                query_id=query_id,
            )
            doc.mark_retrieved()
            yield doc

    async def search(self, query: Query) -> AsyncIterator[Document]:
        """Search PubMed using esearch and efetch."""

        translated_query = self.translator.translate(query)

        # PubMed uses [Tag] syntax. We translated fields like ti:term -> ti:term,
        # but PubMed needs term[ti]. To keep it simple, we let the user write raw pubmed queries
        # or use our generic translator which just emits them as "ti:term".
        # We will parse "ti:term" to "term[ti]" for PubMed specifics here.
        import re

        pubmed_query = re.sub(r"(\w+):([^\s]+)", r"\2[\1]", translated_query)

        params = {
            "db": "pubmed",
            "term": pubmed_query,
            "retmode": "json",
            "retmax": min(query.max_results or 100, 1000),
        }

        # Add year filter to PubMed query syntax if provided
        if query.year_min and query.year_max:
            params["term"] += f" AND {query.year_min}:{query.year_max}[pdat]"
        elif query.year_min:
            params["term"] += f" AND {query.year_min}:3000[pdat]"
        elif query.year_max:
            params["term"] += f" AND 1000:{query.year_max}[pdat]"

        resp = await self.client.get(
            f"{self.base_url}/esearch.fcgi", params=params
        )
        search_response = resp.json()
        pmids = search_response.get("esearchresult", {}).get("idlist", [])

        if not pmids:
            return

        # Fetch details in chunks
        chunk_size = 200
        count = 0
        for i in range(0, len(pmids), chunk_size):
            chunk = pmids[i : i + chunk_size]
            async for doc in self._fetch_details(chunk, query.id):
                yield doc
                count += 1
                if query.max_results and count >= query.max_results:
                    return

    async def get_citations(self, document_id: str) -> AsyncIterator[Document]:
        """Forward Snowballing: Get PMIDs that cite this PMID using elink."""
        params = {
            "dbfrom": "pubmed",
            "linkname": "pubmed_pubmed_citedin",
            "id": document_id,
            "retmode": "json",
        }
        resp = await self.client.get(f"{self.base_url}/elink.fcgi", params=params)
        response = resp.json()

        linkset = response.get("linksets", [])
        if not linkset:
            return

        links = linkset[0].get("linksetdbs", [])
        if not links:
            return

        citing_pmids = links[0].get("links", [])
        async for doc in self._fetch_details(citing_pmids):
            yield doc
