from scholar_search.dedup import Deduplicator
from scholar_search.models import Document, ExternalIds


def test_dedup_metadata_merging():
    doc_openalex = Document(
        title="Attention Is All You Need",
        year=2017,
        provider="openalex",
        external_ids=ExternalIds(
            doi="10.5555/3295222.3295349", openalex_id="W2741809807"
        ),
        url="https://openaccess.thecvf.com/paper.pdf",
        citations_count=60000,
    )
    doc_pubmed = Document(
        title="Attention is all you need.",  # slight title casing/punctuation variation
        year=2017,
        provider="pubmed",
        external_ids=ExternalIds(doi="10.5555/3295222.3295349", pubmed_id="12345678"),
        abstract="We propose a new simple network architecture, the Transformer...",
        mesh_terms=["Neural Networks, Computer", "Artificial Intelligence"],
    )
    doc_s2 = Document(
        title="Attention Is All You Need",
        year=2017,
        provider="semanticscholar",
        external_ids=ExternalIds(
            doi="10.5555/3295222.3295349",
            s2_id="204e3073870fae3d05bcbc2f6a8e263d9b72e776",
        ),
        tldr="The Transformer, a model architecture eschewing recurrence...",
    )

    deduplicator = Deduplicator()
    clusters = deduplicator.deduplicate([doc_openalex, doc_pubmed, doc_s2])

    assert len(clusters) == 1
    rep = clusters[0].representative

    # Verify that representative inherited metadata from all 3 providers
    assert rep.external_ids.doi == "10.5555/3295222.3295349"
    assert rep.external_ids.openalex_id == "W2741809807"
    assert rep.external_ids.pubmed_id == "12345678"
    assert rep.external_ids.s2_id == "204e3073870fae3d05bcbc2f6a8e263d9b72e776"
    assert (
        rep.abstract
        == "We propose a new simple network architecture, the Transformer..."
    )
    assert rep.tldr == "The Transformer, a model architecture eschewing recurrence..."
    assert rep.url == "https://openaccess.thecvf.com/paper.pdf"
    assert rep.citations_count == 60000
    assert "Neural Networks, Computer" in rep.mesh_terms
    assert rep.workspace_id == "SCI-000001"
    assert len(rep.sources) == 3


def test_dedup_fuzzy_matching_with_author_and_year():
    from scholar_search.models import Author

    doc_preprint = Document(
        title="Grounded Language Models for Scientific Discovery",
        year=2023,
        provider="arxiv",
        authors=[Author(family_name="Chen", given_name="Alex")],
        abstract="<jats:p>We introduce a novel grounded RAG architecture.</jats:p>",
    )
    doc_journal = Document(
        title="Grounded Language Models for Scientific Discovery.",
        year=2024,  # +1 year publication delay
        provider="crossref",
        authors=[Author(family_name="Chen", given_name="A.")],
        external_ids=ExternalIds(doi="10.1038/s41586-024-0001"),
    )

    deduplicator = Deduplicator()
    clusters = deduplicator.deduplicate([doc_preprint, doc_journal])

    assert len(clusters) == 1
    rep = clusters[0].representative
    assert rep.workspace_id == "SCI-000001"
    assert rep.external_ids.doi == "10.1038/s41586-024-0001"
    # Abstract should have JATS tags stripped
    assert rep.abstract == "We introduce a novel grounded RAG architecture."
    assert len(rep.sources) == 2


def test_dedup_distinct_papers_not_merged():
    from scholar_search.models import Author

    doc1 = Document(
        title="Deep Learning for Code Generation",
        year=2022,
        provider="arxiv",
        authors=[Author(family_name="Smith")],
    )
    doc2 = Document(
        title="Reinforcement Learning for Code Generation",
        year=2022,
        provider="arxiv",
        authors=[Author(family_name="Smith")],
    )

    deduplicator = Deduplicator()
    clusters = deduplicator.deduplicate([doc1, doc2])

    assert len(clusters) == 2
    assert clusters[0].representative.workspace_id == "SCI-000001"
    assert clusters[1].representative.workspace_id == "SCI-000002"

