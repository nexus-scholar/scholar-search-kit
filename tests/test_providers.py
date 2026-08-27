from unittest.mock import MagicMock, patch

import pytest
import requests
import vcr

from scholar_search.models import Query
from scholar_search.providers.arxiv import ArxivProvider
from scholar_search.providers.biorxiv import BiorxivProvider
from scholar_search.providers.crossref import CrossrefProvider
from scholar_search.providers.openalex import OpenAlexProvider
from scholar_search.providers.pubmed import PubMedProvider
from scholar_search.providers.semanticscholar import SemanticScholarProvider

# Setup VCR to save cassettes in tests/cassettes
my_vcr = vcr.VCR(
    serializer="yaml",
    cassette_library_dir="tests/cassettes",
    record_mode="once",
    match_on=["uri", "method"],
    filter_headers=["authorization"],
)


@pytest.fixture(autouse=True)
def disable_requests_cache():
    with patch(
        "scholar_search.http_client.requests_cache.CachedSession",
        lambda *args, **kwargs: requests.Session(),
    ):
        yield


@my_vcr.use_cassette()
def test_openalex_provider():
    provider = OpenAlexProvider()
    query = Query(text='title:"machine learning" AND year:2023', max_results=5)
    results = list(provider.search(query))
    assert len(results) > 0
    assert results[0].title is not None
    assert results[0].provider == "openalex"


@my_vcr.use_cassette()
def test_pubmed_provider():
    provider = PubMedProvider()
    query = Query(text='title:"machine learning" AND year:2023', max_results=5)
    results = list(provider.search(query))
    assert len(results) > 0
    assert results[0].title is not None
    assert results[0].provider == "pubmed"


@my_vcr.use_cassette()
def test_arxiv_provider():
    provider = ArxivProvider()
    query = Query(text='title:"machine learning"', max_results=5)
    results = list(provider.search(query))
    assert len(results) > 0
    assert results[0].title is not None
    assert results[0].provider == "arxiv"


@my_vcr.use_cassette()
def test_crossref_provider():
    provider = CrossrefProvider()
    query = Query(text='title:"machine learning"', max_results=5)
    results = list(provider.search(query))
    assert len(results) > 0
    assert results[0].title is not None
    assert results[0].provider == "crossref"


def test_semanticscholar_mocked():
    provider = SemanticScholarProvider()
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "data": [
            {
                "paperId": "s2_123",
                "title": "Deep Residual Learning for Image Recognition",
                "year": 2016,
                "citationCount": 150000,
                "externalIds": {"DOI": "10.1109/CVPR.2016.90"},
            }
        ],
        "token": None,
    }
    with patch.object(provider.client, "get", return_value=mock_resp):
        query = Query(text="deep residual learning", max_results=1)
        results = list(provider.search(query))
        assert len(results) == 1
        assert results[0].title == "Deep Residual Learning for Image Recognition"
        assert results[0].external_ids.doi == "10.1109/cvpr.2016.90"
        assert results[0].citations_count == 150000


def test_biorxiv_mocked():
    provider = BiorxivProvider()
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "messages": [{"status": "ok"}],
        "collection": [
            {
                "doi": "10.1101/2020.01.01.123456",
                "title": "CRISPR Genome Editing in Plants",
                "authors": "Smith, J; Doe, A",
                "date": "2020-01-02",
                "server": "biorxiv",
                "abstract": "We describe a novel CRISPR method...",
            }
        ],
    }
    with patch.object(provider.client, "get", return_value=mock_resp):
        query = Query(text="crispr genome", max_results=1)
        results = list(provider.search(query))
        assert len(results) == 1
        assert "CRISPR" in results[0].title
        assert results[0].provider == "biorxiv"
