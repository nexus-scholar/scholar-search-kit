from unittest.mock import MagicMock

from scholar_search.models import Document, ExternalIds
from scholar_search.verifier import DocumentVerifier


def test_verify_document_by_doi():
    mock_crossref = MagicMock()
    mock_crossref.base_url = "https://api.crossref.org/works"
    mock_crossref.client.get.return_value.json.return_value = {
        "message": {
            "title": ["Attention Is All You Need"],
            "DOI": "10.5555/3295222.3295349",
            "published-print": {"date-parts": [[2017]]},
        }
    }
    mock_crossref._normalize_document.return_value = Document(
        title="Attention Is All You Need",
        year=2017,
        external_ids=ExternalIds(doi="10.5555/3295222.3295349"),
    )

    verifier = DocumentVerifier(
        crossref_provider=mock_crossref, openalex_provider=MagicMock()
    )
    doc = Document(
        title="Attention Is All You Need",
        external_ids=ExternalIds(doi="10.5555/3295222.3295349"),
    )

    verified, res_doc, reason = verifier.verify_document(doc)
    assert verified is True
    assert "DOI" in reason
    assert res_doc.year == 2017


def test_verify_document_hallucination_detection():
    mock_crossref = MagicMock()
    mock_crossref.base_url = "https://api.crossref.org/works"
    mock_crossref.client.get.side_effect = Exception("Not found")
    mock_crossref.validate_reference.return_value = None

    mock_openalex = MagicMock()
    mock_openalex.base_url = "https://api.openalex.org/works"
    mock_openalex.client.get.return_value.json.return_value = {"results": []}

    verifier = DocumentVerifier(
        crossref_provider=mock_crossref, openalex_provider=mock_openalex
    )
    fake_doc = Document(
        title="A Fake Hallucinated Paper On Quantum Banana Peels",
        external_ids=ExternalIds(doi="10.1234/fake.doi"),
    )

    verified, res_doc, reason = verifier.verify_document(fake_doc)
    assert verified is False
    assert "Unverified" in reason


def test_hydrate_metadata():
    mock_openalex = MagicMock()
    mock_openalex.base_url = "https://api.openalex.org/works"
    mock_openalex.client.get.return_value.json.return_value = {
        "id": "W123",
        "title": "Real Paper",
    }
    mock_openalex._normalize_document.return_value = Document(
        title="Real Paper",
        abstract="This is the full abstract recovered from OpenAlex.",
        venue="Nature",
        citations_count=120,
        external_ids=ExternalIds(doi="10.1038/real", openalex_id="W123"),
    )

    verifier = DocumentVerifier(openalex_provider=mock_openalex)
    incomplete_doc = Document(
        title="Real Paper", external_ids=ExternalIds(doi="10.1038/real")
    )

    hydrated = verifier.hydrate_metadata(incomplete_doc)
    assert hydrated.abstract == "This is the full abstract recovered from OpenAlex."
    assert hydrated.venue == "Nature"
    assert hydrated.citations_count == 120
