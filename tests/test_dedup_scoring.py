"""Tests for dedup scoring and representative election."""

import pytest

from scholar_search.dedup import Deduplicator
from scholar_search.models import Author, Document, DocumentCluster, ExternalIds


def test_score_based_representative_election():
    """Test that the document with higher score becomes representative.

    The completeness scoring formula awards points for DOI, abstract, venue,
    authors, year, citations, ORCID, and provider weight. The document with
    more metadata should win the election when both match on DOI.
    """
    sparse_doc = Document(
        title="Paper V1",
        year=2024,
        external_ids=ExternalIds(doi="10.1234/test"),
        provider="arxiv",
        # No authors, no abstract, no venue -> lower score
    )
    rich_doc = Document(
        title="Paper V2",
        authors=[Author(family_name="Smith", given_name="John")],
        year=2024,
        abstract="A substantial abstract with more than twenty characters for scoring.",
        venue="NeurIPS",
        external_ids=ExternalIds(doi="10.1234/test"),
        provider="openalex",
        citations_count=42,
    )

    deduplicator = Deduplicator()
    clusters = deduplicator.deduplicate([sparse_doc, rich_doc])

    assert len(clusters) == 1
    rep = clusters[0].representative
    # rich_doc has DOI(+2), abstract(+2), venue(+1), authors(+1), year(+1),
    # citations(+1), not-retracted(+1) = 9 completeness + openalex(5) = 14
    # sparse_doc has DOI(+2), year(+1), not-retracted(+1) = 4 completeness + arxiv(2) = 6
    # rich_doc should win
    assert rep.title == "Paper V2"
    assert (
        rep.abstract
        == "A substantial abstract with more than twenty characters for scoring."
    )


def test_representative_swap_on_higher_score():
    """Test that when a later document scores higher, it replaces the representative.

    The first document encountered becomes the initial representative. If a
    later document with the same DOI scores higher, the representative is swapped.
    """
    low_score_doc = Document(
        title="Sparse Record",
        year=2024,
        external_ids=ExternalIds(doi="10.5555/swap-test"),
        provider="biorxiv",
    )
    high_score_doc = Document(
        title="Rich Record with Full Metadata",
        year=2024,
        abstract="Comprehensive abstract exceeding twenty characters threshold.",
        authors=[
            Author(family_name="Zhang", given_name="Wei", orcid="0000-0001-2345-6789")
        ],
        venue="Nature",
        external_ids=ExternalIds(doi="10.5555/swap-test"),
        provider="openalex",
        citations_count=100,
        references_count=50,
        tldr="Short summary",
    )

    deduplicator = Deduplicator()
    clusters = deduplicator.deduplicate([low_score_doc, high_score_doc])

    assert len(clusters) == 1
    rep = clusters[0].representative
    # high_score_doc should have replaced low_score_doc as representative
    assert rep.title == "Rich Record with Full Metadata"
    assert any(a.orcid for a in rep.authors)


def test_preserves_completeness_metadata_in_merge():
    """Test that dedup merges metadata from non-representative members."""
    doc_with_abstract = Document(
        title="Paper with Abstract",
        year=2024,
        abstract="Detailed abstract about the research methodology and findings.",
        external_ids=ExternalIds(doi="10.1234/merge-test"),
        provider="crossref",
    )
    doc_with_citations = Document(
        title="Paper with Citations",
        year=2024,
        citations_count=200,
        references_count=30,
        external_ids=ExternalIds(doi="10.1234/merge-test"),
        provider="openalex",
    )

    deduplicator = Deduplicator()
    clusters = deduplicator.deduplicate([doc_with_abstract, doc_with_citations])

    assert len(clusters) == 1
    rep = clusters[0].representative
    # Should have merged the best metadata from both sources
    assert (
        rep.abstract == "Detailed abstract about the research methodology and findings."
    )
    assert rep.citations_count == 200
    assert rep.references_count == 30


def test_different_dois_not_deduplicated():
    """Test that documents with different DOIs are kept separate."""
    doc_a = Document(
        title="Paper A",
        external_ids=ExternalIds(doi="10.1234/a"),
    )
    doc_b = Document(
        title="Paper B",
        external_ids=ExternalIds(doi="10.1234/b"),
    )

    deduplicator = Deduplicator()
    clusters = deduplicator.deduplicate([doc_a, doc_b])

    assert len(clusters) == 2


def test_same_arxiv_id_deduplicated():
    """Test that documents matching on arXiv ID are merged via Tier 1."""
    doc_arxiv = Document(
        title="Preprint on Neural Architecture Search",
        year=2023,
        external_ids=ExternalIds(arxiv_id="2301.12345"),
        provider="arxiv",
        authors=[Author(family_name="Lee")],
    )
    doc_published = Document(
        title="Neural Architecture Search: A Survey",
        year=2023,
        abstract="A comprehensive survey of neural architecture search methods.",
        venue="ACM Computing Surveys",
        external_ids=ExternalIds(arxiv_id="2301.12345", doi="10.1145/3600000"),
        provider="crossref",
        authors=[Author(family_name="Lee")],
    )

    deduplicator = Deduplicator()
    clusters = deduplicator.deduplicate([doc_arxiv, doc_published])

    assert len(clusters) == 1
    rep = clusters[0].representative
    # Published version should win: DOI(+2), abstract(+2), venue(+1),
    # authors(+1), year(+1), not-retracted(+1) = 8 + crossref(4) = 12
    # vs arxiv version: authors(+1), year(+1), not-retracted(+1) = 3 + arxiv(2) = 5
    assert rep.title == "Neural Architecture Search: A Survey"
    assert rep.external_ids.doi == "10.1145/3600000"
    assert rep.external_ids.arxiv_id == "2301.12345"


def test_no_doi_keeps_all_documents():
    """Test dedup with documents without DOIs relies on fuzzy title matching."""
    doc_a = Document(
        title="Completely Unrelated Paper About Quantum Computing",
        year=2024,
    )
    doc_b = Document(
        title="Another Unrelated Paper About Climate Change",
        year=2024,
    )

    deduplicator = Deduplicator()
    clusters = deduplicator.deduplicate([doc_a, doc_b])

    assert len(clusters) == 2


def test_empty_document_list():
    """Test dedup with empty input returns empty clusters."""
    deduplicator = Deduplicator()
    clusters = deduplicator.deduplicate([])

    assert clusters == []


def test_single_document():
    """Test dedup with a single document creates one cluster."""
    doc = Document(
        title="Solitary Paper",
        year=2024,
        external_ids=ExternalIds(doi="10.1234/single"),
    )

    deduplicator = Deduplicator()
    clusters = deduplicator.deduplicate([doc])

    assert len(clusters) == 1
    assert clusters[0].representative.title == "Solitary Paper"
    assert clusters[0].size == 1


def test_score_tie_keeps_first_encountered():
    """Test that when two documents have equal scores, the first one wins."""
    doc_first = Document(
        title="Paper First",
        year=2024,
        external_ids=ExternalIds(doi="10.1234/tie"),
        provider="openalex",
    )
    doc_second = Document(
        title="Paper Second",
        year=2024,
        external_ids=ExternalIds(doi="10.1234/tie"),
        provider="openalex",
    )

    deduplicator = Deduplicator()
    clusters = deduplicator.deduplicate([doc_first, doc_second])

    assert len(clusters) == 1
    rep = clusters[0].representative
    # First document should remain representative when scores are equal
    assert rep.title == "Paper First"


def test_get_unique_documents_returns_representatives():
    """Test that get_unique_documents returns only the elected representatives."""
    doc_sparse = Document(
        title="Version A",
        year=2024,
        external_ids=ExternalIds(doi="10.1234/unique"),
        provider="arxiv",
    )
    doc_rich = Document(
        title="Version B",
        year=2024,
        abstract="Full abstract with sufficient length for the scoring threshold.",
        authors=[Author(family_name="Kim", given_name="Soomin")],
        venue="ICML",
        external_ids=ExternalIds(doi="10.1234/unique"),
        provider="openalex",
        citations_count=10,
    )

    deduplicator = Deduplicator()
    unique = deduplicator.get_unique_documents([doc_sparse, doc_rich])

    assert len(unique) == 1
    assert unique[0].title == "Version B"


def test_statistics_after_scoring_election():
    """Test that statistics reflect the dedup outcome after scoring election."""
    doc1 = Document(
        title="Paper Alpha",
        year=2024,
        external_ids=ExternalIds(doi="10.1234/stats-a"),
        provider="openalex",
    )
    doc2 = Document(
        title="Paper Alpha duplicate",
        year=2024,
        external_ids=ExternalIds(doi="10.1234/stats-a"),
        provider="arxiv",
        abstract="Extra information here for scoring differentiation.",
        authors=[Author(family_name="Chen")],
    )
    doc3 = Document(
        title="Paper Beta",
        year=2024,
        external_ids=ExternalIds(doi="10.1234/stats-b"),
        provider="crossref",
    )

    deduplicator = Deduplicator()
    clusters = deduplicator.deduplicate([doc1, doc2, doc3])
    stats = deduplicator.get_statistics(clusters)

    assert stats["total_documents"] == 3
    assert stats["unique_documents"] == 2
    assert stats["duplicates"] == 1
    assert stats["duplicate_rate"] == pytest.approx(1 / 3)
