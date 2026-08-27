"""Deterministic document deduplication and metadata merging."""

import re
from difflib import SequenceMatcher

from .models import Document, DocumentCluster


def _title_key(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


class Deduplicator:
    """Cluster documents by identifiers, then conservative title matching, merging metadata."""

    def deduplicate(self, documents: list[Document]) -> list[DocumentCluster]:
        clusters: list[DocumentCluster] = []
        for document in documents:
            match = self._find_match(document, clusters)
            if match is None:
                match = DocumentCluster(len(clusters) + 1, document, [document])
                clusters.append(match)
            else:
                match.members.append(document)
                self._merge_metadata(match.representative, document)
            document.cluster_id = match.cluster_id
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
                if self._same_identifier(document, member):
                    return cluster

                doc_title = _title_key(document.title)
                member_title = _title_key(member.title)
                if doc_title and member_title:
                    if SequenceMatcher(None, doc_title, member_title).ratio() >= 0.97:
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
    def _merge_metadata(rep: Document, source: Document) -> None:
        """Enrich the representative document with missing metadata from a duplicate."""
        # IDs
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

        # Text fields
        if not rep.abstract and source.abstract:
            rep.abstract = source.abstract
        if not rep.venue and source.venue:
            rep.venue = source.venue
        if not rep.url and source.url:
            rep.url = source.url
        if not rep.year and source.year:
            rep.year = source.year
        if not rep.tldr and source.tldr:
            rep.tldr = source.tldr

        # Authors
        if not rep.authors and source.authors:
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
