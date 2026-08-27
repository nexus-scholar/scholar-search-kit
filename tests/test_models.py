from datetime import UTC

from scholar_search.models import Author, Document, DocumentCluster, ExternalIds, Query


def test_external_ids_normalization():
    cases = [
        ("https://doi.org/10.1000/182", "10.1000/182"),
        ("http://doi.org/10.1000/182", "10.1000/182"),
        ("DOI:10.1000/182", "10.1000/182"),
        ("doi: 10.1000/182", "10.1000/182"),
        ("10.1000/182", "10.1000/182"),
        ("HTTPS://DOI.ORG/10.1000/ABC", "10.1000/abc"),
    ]
    for raw, expected in cases:
        ids = ExternalIds(doi=raw)
        assert ids.doi == expected


def test_author_properties():
    a1 = Author(family_name="Turing", given_name="Alan")
    assert a1.full_name == "Alan Turing"

    a2 = Author(family_name="Euclid")
    assert a2.full_name == "Euclid"


def test_document_defaults_and_retrieval():
    doc = Document(title="Computing Machinery and Intelligence", year=1950)
    assert doc.external_ids is not None
    assert doc.authors == []
    assert doc.retrieved_at is None

    doc.mark_retrieved()
    assert doc.retrieved_at is not None
    assert doc.retrieved_at.tzinfo == UTC


def test_query_model():
    q = Query(
        id="Q01",
        text='"deep learning" AND robotics',
        year_min=2020,
        year_max=2024,
        max_results=100,
    )
    assert q.id == "Q01"
    assert q.year_min == 2020
    assert q.year_max == 2024
    assert q.max_results == 100


def test_document_cluster():
    d1 = Document(
        "Paper A", external_ids=ExternalIds(doi="10.1/abc"), provider="openalex"
    )
    d2 = Document(
        "Paper A", external_ids=ExternalIds(doi="10.1/abc"), provider="crossref"
    )

    cluster = DocumentCluster(cluster_id=1, representative=d1, members=[d1, d2])

    assert cluster.size == 2
    assert cluster.confidence == 1.0
    assert d1 in cluster.members
    assert d2 in cluster.members
