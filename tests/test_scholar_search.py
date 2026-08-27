from scholar_search.dedup import Deduplicator
from scholar_search.models import Document, ExternalIds


def test_doi_is_normalized_and_duplicates_clustered():
    first = Document(
        "A Study", external_ids=ExternalIds(doi="https://doi.org/10.1/ABC")
    )
    second = Document("A Study", external_ids=ExternalIds(doi="10.1/abc"))

    clusters = Deduplicator().deduplicate([first, second])

    assert len(clusters) == 1
    assert clusters[0].size == 2
    assert first.cluster_id == second.cluster_id == 1
