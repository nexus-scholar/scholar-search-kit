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
