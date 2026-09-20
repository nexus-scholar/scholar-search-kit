"""Tests for AbstractHydrator."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from scholar_search.enrichment import AbstractHydrator
from scholar_search.models import Document, ExternalIds


@pytest.fixture
def mock_http_client():
    """Create a mock AcademicHttpClient."""
    client = AsyncMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    return client


@pytest.fixture
def hydrator(mock_http_client):
    """Create AbstractHydrator with mock client."""
    return AbstractHydrator(mock_http_client)


# ---------------------------------------------------------------------------
# _reconstruct_abstract (static method)
# ---------------------------------------------------------------------------


def test_reconstruct_abstract():
    """Test OpenAlex inverted index reconstruction."""
    inverted_index = {
        "machine": [0],
        "learning": [1],
        "is": [2],
        "useful": [3],
        "for": [4],
        "healthcare": [5],
    }

    result = AbstractHydrator._reconstruct_abstract(inverted_index)

    assert result == "machine learning is useful for healthcare"


def test_reconstruct_abstract_empty():
    """Test empty inverted index."""
    result = AbstractHydrator._reconstruct_abstract({})
    assert result == ""


def test_reconstruct_abstract_none():
    """Test None inverted index."""
    result = AbstractHydrator._reconstruct_abstract(None)
    assert result == ""


def test_reconstruct_abstract_single_word():
    """Test single word inverted index."""
    result = AbstractHydrator._reconstruct_abstract({"hello": [0]})
    assert result == "hello"


def test_reconstruct_abstract_disordered_positions():
    """Test positions not given in sorted order."""
    inverted_index = {
        "world": [3],
        "hello": [0],
        "foo": [2],
        "bar": [1],
    }
    result = AbstractHydrator._reconstruct_abstract(inverted_index)
    assert result == "hello bar foo world"


# ---------------------------------------------------------------------------
# _hydrate_from_s2
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_hydrate_from_s2_empty_dois(hydrator):
    """Test S2 hydration with no DOIs returns empty."""
    result = await hydrator._hydrate_from_s2([])
    assert result == {}


@pytest.mark.asyncio
async def test_hydrate_from_s2_success(hydrator, mock_http_client):
    """Test successful S2 hydration extracts abstract by DOI."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "paperId": "abc123",
            "abstract": "A test abstract",
            "externalIds": {"DOI": "10.1234/test"},
        }
    ]
    mock_http_client.post.return_value = mock_response

    result = await hydrator._hydrate_from_s2(["10.1234/test"])

    assert "10.1234/test" in result
    assert result["10.1234/test"] == "A test abstract"


@pytest.mark.asyncio
async def test_hydrate_from_s2_no_abstract(hydrator, mock_http_client):
    """Test S2 returns paper without abstract."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "paperId": "abc123",
            "abstract": None,
            "externalIds": {"DOI": "10.1234/test"},
        }
    ]
    mock_http_client.post.return_value = mock_response

    result = await hydrator._hydrate_from_s2(["10.1234/test"])

    assert result == {}


@pytest.mark.asyncio
async def test_hydrate_from_s2_no_doi_in_response(hydrator, mock_http_client):
    """Test S2 returns paper without DOI in externalIds."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "paperId": "abc123",
            "abstract": "An abstract",
            "externalIds": {},
        }
    ]
    mock_http_client.post.return_value = mock_response

    result = await hydrator._hydrate_from_s2(["10.1234/test"])

    assert result == {}


@pytest.mark.asyncio
async def test_hydrate_from_s2_http_error(hydrator, mock_http_client):
    """Test S2 hydration returns empty on HTTP error."""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_http_client.post.return_value = mock_response

    result = await hydrator._hydrate_from_s2(["10.1234/test"])

    assert result == {}


@pytest.mark.asyncio
async def test_hydrate_from_s2_exception(hydrator, mock_http_client):
    """Test S2 hydration returns empty on exception."""
    mock_http_client.post.side_effect = Exception("network error")

    result = await hydrator._hydrate_from_s2(["10.1234/test"])

    assert result == {}


# ---------------------------------------------------------------------------
# _hydrate_from_openalex
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_hydrate_from_openalex_empty_dois(hydrator):
    """Test OpenAlex hydration with no DOIs returns empty."""
    result = await hydrator._hydrate_from_openalex([])
    assert result == {}


@pytest.mark.asyncio
async def test_hydrate_from_openalex_success(hydrator, mock_http_client):
    """Test successful OpenAlex hydration reconstructs abstract from inverted index."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [
            {
                "abstract_inverted_index": {
                    "test": [0],
                    "abstract": [1],
                }
            }
        ]
    }
    mock_http_client.get.return_value = mock_response

    result = await hydrator._hydrate_from_openalex(["10.1234/test"])

    assert "10.1234/test" in result
    assert result["10.1234/test"] == "test abstract"


@pytest.mark.asyncio
async def test_hydrate_from_openalex_no_results(hydrator, mock_http_client):
    """Test OpenAlex hydration with empty results list."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"results": []}
    mock_http_client.get.return_value = mock_response

    result = await hydrator._hydrate_from_openalex(["10.1234/test"])

    assert result == {}


@pytest.mark.asyncio
async def test_hydrate_from_openalex_no_inverted_index(hydrator, mock_http_client):
    """Test OpenAlex result without abstract_inverted_index."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"results": [{"title": "Some work"}]}
    mock_http_client.get.return_value = mock_response

    result = await hydrator._hydrate_from_openalex(["10.1234/test"])

    assert result == {}


@pytest.mark.asyncio
async def test_hydrate_from_openalex_http_error(hydrator, mock_http_client):
    """Test OpenAlex hydration skips on HTTP error."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_http_client.get.return_value = mock_response

    result = await hydrator._hydrate_from_openalex(["10.1234/test"])

    assert result == {}


@pytest.mark.asyncio
async def test_hydrate_from_openalex_exception(hydrator, mock_http_client):
    """Test OpenAlex hydration skips on exception."""
    mock_http_client.get.side_effect = Exception("connection error")

    result = await hydrator._hydrate_from_openalex(["10.1234/test"])

    assert result == {}


# ---------------------------------------------------------------------------
# hydrate_missing_abstracts (integration of S2 + OpenAlex)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_hydrate_missing_abstracts_empty(hydrator):
    """Test hydration with empty document list."""
    result, stats = await hydrator.hydrate_missing_abstracts([])

    assert result == []
    assert stats["hydrated"] == 0
    assert stats["attempted"] == 0


@pytest.mark.asyncio
async def test_hydrate_missing_abstracts_all_have_abstract(hydrator):
    """Test hydration when all documents already have abstracts."""
    doc = Document(
        title="Already has abstract",
        abstract="I already exist",
        external_ids=ExternalIds(doi="10.1234/test"),
    )

    result, stats = await hydrator.hydrate_missing_abstracts([doc])

    assert stats["attempted"] == 0
    assert stats["hydrated"] == 0
    assert doc.abstract == "I already exist"


@pytest.mark.asyncio
async def test_hydrate_missing_abstracts_no_doi(hydrator):
    """Test hydration for documents without DOIs (cannot be looked up)."""
    doc = Document(title="No DOI", abstract=None)

    result, stats = await hydrator.hydrate_missing_abstracts([doc])

    assert stats["attempted"] == 0
    assert doc.abstract is None


@pytest.mark.asyncio
async def test_hydrate_missing_abstracts_s2_success(hydrator, mock_http_client):
    """Test full pipeline: S2 returns abstract, no OpenAlex fallback needed."""
    doc = Document(
        title="Needs abstract",
        abstract=None,
        external_ids=ExternalIds(doi="10.1234/test"),
    )

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "paperId": "abc",
            "abstract": "Hydrated from S2",
            "externalIds": {"DOI": "10.1234/test"},
        }
    ]
    mock_http_client.post.return_value = mock_response

    result, stats = await hydrator.hydrate_missing_abstracts([doc])

    assert stats["hydrated"] == 1
    assert stats["failed"] == 0
    assert doc.abstract == "Hydrated from S2"


@pytest.mark.asyncio
async def test_hydrate_missing_abstracts_fallback_to_openalex(
    hydrator, mock_http_client
):
    """Test fallback: S2 misses, OpenAlex fills in."""
    doc = Document(
        title="Needs abstract",
        abstract=None,
        external_ids=ExternalIds(doi="10.1234/test"),
    )

    # S2 returns empty
    s2_response = MagicMock()
    s2_response.status_code = 200
    s2_response.json.return_value = []

    # OpenAlex returns inverted index
    oa_response = MagicMock()
    oa_response.status_code = 200
    oa_response.json.return_value = {
        "results": [
            {
                "abstract_inverted_index": {
                    "fallback": [0],
                    "abstract": [1],
                }
            }
        ]
    }

    mock_http_client.post.return_value = s2_response
    mock_http_client.get.return_value = oa_response

    result, stats = await hydrator.hydrate_missing_abstracts([doc])

    assert stats["hydrated"] == 1
    assert doc.abstract == "fallback abstract"


@pytest.mark.asyncio
async def test_hydrate_missing_abstracts_both_fail(hydrator, mock_http_client):
    """Test both S2 and OpenAlex fail -> document stays without abstract."""
    doc = Document(
        title="Unhydratable",
        abstract=None,
        external_ids=ExternalIds(doi="10.1234/test"),
    )

    # S2 returns empty
    s2_response = MagicMock()
    s2_response.status_code = 200
    s2_response.json.return_value = []

    # OpenAlex returns no results
    oa_response = MagicMock()
    oa_response.status_code = 200
    oa_response.json.return_value = {"results": []}

    mock_http_client.post.return_value = s2_response
    mock_http_client.get.return_value = oa_response

    result, stats = await hydrator.hydrate_missing_abstracts([doc])

    assert stats["hydrated"] == 0
    assert stats["failed"] == 1
    assert doc.abstract is None


@pytest.mark.asyncio
async def test_hydrate_missing_abstracts_mixed_documents(hydrator, mock_http_client):
    """Test hydration with mix of: already has abstract, no DOI, needs hydration."""
    doc_with_abstract = Document(
        title="Has abstract",
        abstract="Already there",
        external_ids=ExternalIds(doi="10.1111/aaa"),
    )
    doc_no_doi = Document(title="No DOI", abstract=None)
    doc_needs = Document(
        title="Needs it",
        abstract=None,
        external_ids=ExternalIds(doi="10.2222/bbb"),
    )

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "paperId": "p1",
            "abstract": "Looked up abstract",
            "externalIds": {"DOI": "10.2222/bbb"},
        }
    ]
    mock_http_client.post.return_value = mock_response

    result, stats = await hydrator.hydrate_missing_abstracts(
        [doc_with_abstract, doc_no_doi, doc_needs]
    )

    assert stats["attempted"] == 1  # only doc_needs needs hydration
    assert stats["hydrated"] == 1
    assert doc_with_abstract.abstract == "Already there"
    assert doc_no_doi.abstract is None
    assert doc_needs.abstract == "Looked up abstract"
