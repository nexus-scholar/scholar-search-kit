"""Verification and metadata hydration engine for academic literature."""

import logging
from difflib import SequenceMatcher
from typing import Any

from .dedup import _title_key
from .models import Document
from .providers.crossref import CrossrefProvider
from .providers.openalex import OpenAlexProvider

logger = logging.getLogger(__name__)


class DocumentVerifier:
    """
    Verifies the existence of documents against Crossref & OpenAlex
    to detect hallucinations and hydates missing metadata.
    """

    def __init__(
        self,
        crossref_provider: CrossrefProvider | None = None,
        openalex_provider: OpenAlexProvider | None = None,
    ):
        self.crossref = crossref_provider or CrossrefProvider()
        self.openalex = openalex_provider or OpenAlexProvider()

    async def verify_document(self, doc: Document) -> tuple[bool, Document, str]:
        """
        Verifies if a document is real.
        Returns (is_verified, hydrated_document, explanation).
        """
        # 1. Verification by existing DOI
        if doc.external_ids.doi:
            try:
                # Query Crossref by DOI
                clean_doi = doc.external_ids.doi.strip()
                url = f"{self.crossref.base_url}/{clean_doi}"
                resp = await self.crossref.client.get(url)
                response = resp.json()
                item = response.get("message", {})
                if item:
                    verified_doc = self.crossref._normalize_document(item)
                    return True, verified_doc, f"Verified via DOI ({clean_doi})"
            except Exception as e:
                logger.debug(f"DOI verification failed for {doc.external_ids.doi}: {e}")

        # 2. Verification by Title / Bibliographic query in Crossref
        if doc.title and doc.title != "Untitled":
            try:
                matched_doc = await self.crossref.validate_reference(doc.title)
                if matched_doc:
                    ratio = SequenceMatcher(
                        None, _title_key(doc.title), _title_key(matched_doc.title)
                    ).ratio()
                    if ratio >= 0.90:
                        return (
                            True,
                            matched_doc,
                            f"Verified via Crossref matching ({ratio:.0%} title match)",
                        )
            except Exception as e:
                logger.debug(f"Crossref title search failed: {e}")

        # 3. Fallback to OpenAlex Title Search
        if doc.title and doc.title != "Untitled":
            try:
                url = f"{self.openalex.base_url}"
                params = {"search": doc.title, "per-page": 1}
                resp = await self.openalex.client.get(url, params=params)
                response = resp.json()
                results = response.get("results", [])
                if results:
                    candidate = self.openalex._normalize_document(results[0])
                    ratio = SequenceMatcher(
                        None, _title_key(doc.title), _title_key(candidate.title)
                    ).ratio()
                    if ratio >= 0.90:
                        return (
                            True,
                            candidate,
                            f"Verified via OpenAlex matching ({ratio:.0%} title match)",
                        )
            except Exception as e:
                logger.debug(f"OpenAlex title search failed: {e}")

        return False, doc, "Unverified: Record not found in Crossref or OpenAlex"

    async def hydrate_metadata(self, doc: Document) -> Document:
        """Hydrates missing fields (abstract, OA URL, venue, citations) from OpenAlex."""
        doi = doc.external_ids.doi
        if not doi:
            return doc

        try:
            url = f"{self.openalex.base_url}/https://doi.org/{doi}"
            resp = await self.openalex.client.get(url)
            response = resp.json()
            if response:
                openalex_doc = self.openalex._normalize_document(response)

                # Enrich fields
                if not doc.abstract and openalex_doc.abstract:
                    doc.abstract = openalex_doc.abstract
                if not doc.venue and openalex_doc.venue:
                    doc.venue = openalex_doc.venue
                if not doc.url and openalex_doc.url:
                    doc.url = openalex_doc.url
                if not doc.year and openalex_doc.year:
                    doc.year = openalex_doc.year
                if not doc.authors and openalex_doc.authors:
                    doc.authors = openalex_doc.authors
                if doc.citations_count is None:
                    doc.citations_count = openalex_doc.citations_count
                if doc.references_count is None:
                    doc.references_count = openalex_doc.references_count
                if (
                    not doc.external_ids.openalex_id
                    and openalex_doc.external_ids.openalex_id
                ):
                    doc.external_ids.openalex_id = openalex_doc.external_ids.openalex_id
        except Exception as e:
            logger.debug(f"Hydration failed for DOI {doi}: {e}")

        return doc

    async def process_batch(
        self, documents: list[Document], verify: bool = True, enrich: bool = True
    ) -> tuple[list[Document], list[dict[str, Any]]]:
        """
        Processes a batch of documents with verification and hydration.
        Returns (processed_documents, audit_log).
        """
        processed_docs: list[Document] = []
        audit_log: list[dict[str, Any]] = []

        for doc in documents:
            is_verified = True
            note = "Not checked"
            current_doc = doc

            if verify:
                is_verified, current_doc, note = await self.verify_document(doc)

            if is_verified and enrich:
                current_doc = await self.hydrate_metadata(current_doc)

            processed_docs.append(current_doc)
            audit_log.append(
                {
                    "title": doc.title,
                    "input_doi": doc.external_ids.doi,
                    "verified": is_verified,
                    "resolved_doi": current_doc.external_ids.doi,
                    "status": note,
                }
            )

        return processed_docs, audit_log
