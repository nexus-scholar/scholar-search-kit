from scholar_search.dedup import Deduplicator
from scholar_search.models import Document, ExternalIds, Query
from scholar_search.providers import InMemoryProvider


def test_doi_is_normalized_and_duplicates_clustered():
    first = Document("A Study", external_ids=ExternalIds(doi="https://doi.org/10.1/ABC"))
    second = Document("A Study", external_ids=ExternalIds(doi="10.1/abc"))

    clusters = Deduplicator().deduplicate([first, second])

    assert len(clusters) == 1
    assert clusters[0].size == 2
    assert first.cluster_id == second.cluster_id == 1


def test_in_memory_provider_filters_and_records_query():
    provider = InMemoryProvider([
        Document("Harness safety", year=2024),
        Document("Other topic", year=2020),
    ])

    results = list(provider.search(Query(id="Q1", text="harness", year_min=2023)))

    assert [document.title for document in results] == ["Harness safety"]
    assert results[0].query_id == "Q1"
    assert results[0].retrieved_at is not None