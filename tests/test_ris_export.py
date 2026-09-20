"""Tests for RIS exporter."""

import pytest
from pathlib import Path

from scholar_search.export import Exporter


@pytest.fixture
def exporter():
    return Exporter()


@pytest.fixture
def sample_documents():
    """Create sample Document objects for testing."""
    from scholar_search.models import Document, Author, ExternalIds

    docs = [
        Document(
            title="Machine Learning in Healthcare",
            authors=[
                Author(family_name="Smith", given_name="John"),
                Author(family_name="Doe", given_name="Jane"),
            ],
            year=2024,
            venue="Journal of Medical AI",
            abstract="A review of ML applications in healthcare.",
            external_ids=ExternalIds(doi="10.1234/test1"),
            url="https://example.com/paper1",
            sources=[{"provider": "openalex"}],
        ),
        Document(
            title="Deep Learning for NLP",
            authors=[Author(family_name="Brown", given_name="Alice")],
            year=2023,
            venue="Conference on AI",
            abstract="NLP techniques using deep learning.",
            external_ids=ExternalIds(doi="10.1234/test2", arxiv_id="2301.12345"),
            sources=[{"provider": "semantic_scholar"}],
        ),
    ]
    return docs


def test_ris_creates_file(exporter, sample_documents, tmp_path):
    """RIS export creates output file."""
    output = tmp_path / "test.ris"
    result = exporter.ris(sample_documents, output)

    assert result.exists()
    assert result.suffix == ".ris"


def test_ris_enforces_suffix(exporter, sample_documents, tmp_path):
    """RIS export enforces .ris suffix."""
    output = tmp_path / "test.txt"
    result = exporter.ris(sample_documents, output)

    assert result.suffix == ".ris"


def test_ris_content_format(exporter, sample_documents, tmp_path):
    """RIS output has correct format."""
    output = tmp_path / "test.ris"
    result = exporter.ris(sample_documents, output)

    content = result.read_text(encoding="utf-8")

    # Check RIS tags present
    assert "TY  - JOUR" in content  # Journal type
    assert "TI  - Machine Learning in Healthcare" in content
    assert "AU  - Smith, John" in content
    assert "PY  - 2024" in content
    assert "JO  - Journal of Medical AI" in content
    assert "AB  - A review of ML applications in healthcare." in content
    assert "DO  - 10.1234/test1" in content
    assert "UR  - https://example.com/paper1" in content
    assert "DB  - openalex" in content
    assert "ER  - " in content


def test_ris_type_detection(exporter, sample_documents, tmp_path):
    """RIS type detection works correctly."""
    output = tmp_path / "test.ris"
    result = exporter.ris(sample_documents, output)

    content = result.read_text(encoding="utf-8")

    # First doc is journal (has "journal" in venue)
    assert "TY  - JOUR" in content
    # Second doc is conference (has "conf" in venue)
    assert "TY  - CONF" in content


def test_ris_arxiv_field(exporter, sample_documents, tmp_path):
    """RIS export includes arXiv ID in C1 field."""
    output = tmp_path / "test.ris"
    result = exporter.ris(sample_documents, output)

    content = result.read_text(encoding="utf-8")
    assert "C1  - arXiv:2301.12345" in content


def test_ris_empty_documents(exporter, tmp_path):
    """RIS export handles empty document list."""
    output = tmp_path / "test.ris"
    result = exporter.ris([], output)

    assert result.exists()
    assert result.read_text(encoding="utf-8") == ""


def test_ris_creates_parent_dirs(exporter, sample_documents, tmp_path):
    """RIS export creates parent directories."""
    output = tmp_path / "subdir" / "test.ris"
    result = exporter.ris(sample_documents, output)

    assert result.exists()


def test_ris_general_type_fallback(exporter, tmp_path):
    """RIS export uses GEN type when venue is not journal or conference."""
    from scholar_search.models import Document, ExternalIds

    docs = [
        Document(
            title="A General Paper",
            year=2022,
            venue="arXiv preprint",
        )
    ]
    output = tmp_path / "test.ris"
    result = exporter.ris(docs, output)

    content = result.read_text(encoding="utf-8")
    assert "TY  - GEN" in content


def test_ris_multiple_authors(exporter, tmp_path):
    """RIS export handles documents with multiple authors."""
    from scholar_search.models import Document, Author, ExternalIds

    docs = [
        Document(
            title="Multi-Author Paper",
            authors=[
                Author(family_name="Alpha", given_name="A"),
                Author(family_name="Beta", given_name="B"),
                Author(family_name="Gamma", given_name="C"),
            ],
            year=2023,
            venue="Nature",
        )
    ]
    output = tmp_path / "test.ris"
    result = exporter.ris(docs, output)

    content = result.read_text(encoding="utf-8")
    assert "AU  - Alpha, A" in content
    assert "AU  - Beta, B" in content
    assert "AU  - Gamma, C" in content


def test_ris_no_optional_fields(exporter, tmp_path):
    """RIS export omits tags for absent optional fields."""
    from scholar_search.models import Document

    docs = [Document(title="Minimal Paper")]
    output = tmp_path / "test.ris"
    result = exporter.ris(docs, output)

    content = result.read_text(encoding="utf-8")
    assert "TI  - Minimal Paper" in content
    assert "PY  -" not in content
    assert "AB  -" not in content
    assert "DO  -" not in content
    assert "UR  -" not in content
    assert "C1  -" not in content
    assert "JO  -" not in content
    assert "T2  -" not in content


def test_ris_venue_tag_switch(exporter, tmp_path):
    """RIS export uses JO for journals, T2 for non-journals."""
    from scholar_search.models import Document

    jour_doc = Document(title="Journal Paper", venue="Journal of Physics")
    conf_doc = Document(title="Conference Paper", venue="NeurIPS")
    gen_doc = Document(title="Generic Paper", venue="Some Venue")

    output = tmp_path / "test.ris"
    result = exporter.ris([jour_doc, conf_doc, gen_doc], output)

    content = result.read_text(encoding="utf-8")
    # Journal uses JO
    assert "JO  - Journal of Physics" in content
    # Conference uses T2
    assert "T2  - NeurIPS" in content
    # Generic also uses T2
    assert "T2  - Some Venue" in content


def test_ris_doi_normalization(exporter, tmp_path):
    """RIS export uses normalized DOI from ExternalIds."""
    from scholar_search.models import Document, ExternalIds

    docs = [
        Document(
            title="DOI Test",
            external_ids=ExternalIds(doi="https://doi.org/10.1000/test123"),
        )
    ]
    output = tmp_path / "test.ris"
    result = exporter.ris(docs, output)

    content = result.read_text(encoding="utf-8")
    # ExternalIds normalizes the DOI by stripping prefix and lowering
    assert "DO  - 10.1000/test123" in content
