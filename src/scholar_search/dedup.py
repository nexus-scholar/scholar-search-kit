"""Deterministic document deduplication and non-destructive metadata fusion."""

import re
from difflib import SequenceMatcher

from .models import Document, DocumentCluster


def _title_key(title: str) -> str:
    """Normalizes a title by removing non-alphanumeric characters and extra whitespace."""
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def _first_author_surname(doc: Document) -> str | None:
    """Extracts normalized first author surname if present."""
    if doc.authors:
        return doc.authors[0].family_name.lower().strip()
    return None


class Deduplicator:
    """
    Two-tier deterministic deduplication and non-destructive metadata fusion engine:
      Tier 1: Canonical Persistent Identifiers (DOI, arXiv ID, PMID, OpenAlex ID, S2 ID)
      Tier 2: Fuzzy lexical title normalization (>= 97%) + author surname match + year tolerance (+/- 1 year)
    """

    def deduplicate(self, documents: list[Document]) -> list[DocumentCluster]:
        clusters: list[DocumentCluster] = []
        for document in documents:
            match = self._find_match(document, clusters)
            if match is None:
                cluster_id = len(clusters) + 1
                document.workspace_id = f"SCI-{cluster_id:06d}"
                match = DocumentCluster(cluster_id, document, [document])
                clusters.append(match)
            else:
                match.members.append(document)
                self._merge_metadata(match.representative, document)
            document.cluster_id = match.cluster_id
            document.workspace_id = match.representative.workspace_id
        return clusters

    def get_unique_documents(self, documents: list[Document]) -> list[Document]:
        return [cluster.representative for cluster in self.deduplicate(documents)]

    def get_statistics(self, clusters: list[DocumentCluster]) -> dict[str, int | float]:
        total = sum(cluster.size for cluster in clusters)
        unique = len(clusters)
        duplicates = total - unique
        return {
            "total_documents": total,
            "unique_documents": unique,
            "duplicates": duplicates,
            "duplicate_rate": duplicates / total if total else 0.0,
        }

    def _find_match(
        self, document: Document, clusters: list[DocumentCluster]
    ) -> DocumentCluster | None:
        for cluster in clusters:
            for member in cluster.members:
                # Tier 1: Canonical Persistent Identifiers
                if self._same_identifier(document, member):
                    return cluster

                # Tier 2: Fuzzy Title Normalization + Author + Year Tolerance
                if self._fuzzy_match(document, member):
                    return cluster
        return None

    @staticmethod
    def _same_identifier(left: Document, right: Document) -> bool:
        left_ids = left.external_ids
        right_ids = right.external_ids
        return bool(
            (left_ids.doi and left_ids.doi == right_ids.doi)
            or (left_ids.arxiv_id and left_ids.arxiv_id == right_ids.arxiv_id)
            or (left_ids.pubmed_id and left_ids.pubmed_id == right_ids.pubmed_id)
            or (left_ids.openalex_id and left_ids.openalex_id == right_ids.openalex_id)
            or (left_ids.s2_id and left_ids.s2_id == right_ids.s2_id)
        )

    @staticmethod
    def _fuzzy_match(left: Document, right: Document) -> bool:
        left_title = _title_key(left.title)
        right_title = _title_key(right.title)
        if not left_title or not right_title:
            return False

        ratio = SequenceMatcher(None, left_title, right_title).ratio()
        if ratio < 0.97:
            return False

        # Check year tolerance (+/- 1 year) if both have publication year
        if left.year and right.year:
            if abs(left.year - right.year) > 1:
                return False

        # Check author surname match if both have authors
        left_author = _first_author_surname(left)
        right_author = _first_author_surname(right)
        if left_author and right_author:
            # Surnames should match or one contain the other (to handle prefixes like de/van/von)
            if left_author != right_author and left_author not in right_author and right_author not in left_author:
                return False

        return True

    @staticmethod
    def _merge_metadata(rep: Document, source: Document) -> None:
        """Enrich the representative document with missing metadata and provenance from a duplicate."""
        # Merge Persistent Identifiers
        if not rep.external_ids.doi and source.external_ids.doi:
            rep.external_ids.doi = source.external_ids.doi
        if not rep.external_ids.arxiv_id and source.external_ids.arxiv_id:
            rep.external_ids.arxiv_id = source.external_ids.arxiv_id
        if not rep.external_ids.pubmed_id and source.external_ids.pubmed_id:
            rep.external_ids.pubmed_id = source.external_ids.pubmed_id
        if not rep.external_ids.openalex_id and source.external_ids.openalex_id:
            rep.external_ids.openalex_id = source.external_ids.openalex_id
        if not rep.external_ids.s2_id and source.external_ids.s2_id:
            rep.external_ids.s2_id = source.external_ids.s2_id

        # Merge Provenance Sources
        for src in source.sources:
            if src not in rep.sources:
                rep.sources.append(src)

        # Merge OA Locations
        for oa in source.oa_locations:
            if oa not in rep.oa_locations:
                rep.oa_locations.append(oa)

        # Text fields: Prefer longer / cleaner abstract
        if source.abstract:
            if not rep.abstract or len(source.abstract) > len(rep.abstract):
                rep.abstract = source.abstract

        if not rep.venue and source.venue:
            rep.venue = source.venue
        if not rep.url and source.url:
            rep.url = source.url
        if not rep.year and source.year:
            rep.year = source.year
        if not rep.tldr and source.tldr:
            rep.tldr = source.tldr

        # Authors: Prefer richer author list
        if len(source.authors) > len(rep.authors):
            rep.authors = list(source.authors)

        # Numerical fields (take maximum)
        if source.citations_count is not None:
            if (
                rep.citations_count is None
                or source.citations_count > rep.citations_count
            ):
                rep.citations_count = source.citations_count

        if source.references_count is not None:
            if (
                rep.references_count is None
                or source.references_count > rep.references_count
            ):
                rep.references_count = source.references_count

        # Lists (deduplicate union)
        for mesh in source.mesh_terms:
            if mesh not in rep.mesh_terms:
                rep.mesh_terms.append(mesh)

        for intent in source.citation_intents:
            if intent not in rep.citation_intents:
                rep.citation_intents.append(intent)
