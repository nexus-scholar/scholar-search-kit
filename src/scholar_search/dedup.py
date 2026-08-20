"""Deterministic document deduplication."""

import re
from difflib import SequenceMatcher

from .models import Document, DocumentCluster


def _title_key(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


class Deduplicator:
    """Cluster documents by identifiers, then conservative title matching."""

    def deduplicate(self, documents: list[Document]) -> list[DocumentCluster]:
        clusters: list[DocumentCluster] = []
        for document in documents:
            match = self._find_match(document, clusters)
            if match is None:
                match = DocumentCluster(len(clusters) + 1, document, [document])
                clusters.append(match)
            else:
                match.members.append(document)
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
                if SequenceMatcher(None, _title_key(document.title), _title_key(member.title)).ratio() >= 0.97:
                    return cluster
        return None

    @staticmethod
    def _same_identifier(left: Document, right: Document) -> bool:
        left_ids = left.external_ids
        right_ids = right.external_ids
        return bool(
            (left_ids.doi and left_ids.doi == right_ids.doi)
            or (left_ids.arxiv_id and left_ids.arxiv_id == right_ids.arxiv_id)
        )