from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from scholar_search.models import Query
from scholar_search.providers.arxiv import ArxivProvider
from scholar_search.providers.biorxiv import BiorxivProvider
from scholar_search.providers.crossref import CrossrefProvider
from scholar_search.providers.openalex import OpenAlexProvider
from scholar_search.providers.pubmed import PubMedProvider
from scholar_search.providers.semanticscholar import SemanticScholarProvider


@pytest.mark.asyncio
async def test_openalex_provider():
    provider = OpenAlexProvider()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "results": [
            {
                "id": "https://openalex.org/W2741809807",
                "title": "Attention Is All You Need",
                "publication_year": 2017,
                "ids": {"doi": "https://doi.org/10.5555/3295222.3295349", "openalex": "W2741809807"},
                "authorships": [{"author": {"display_name": "Ashish Vaswani"}}],
                "cited_by_count": 145000,
                "referenced_works": ["W1", "W2"],
            }
        ],
        "meta": {"next_cursor": None},
    }
    with patch.object(provider.client, "get", new_callable=AsyncMock, return_value=mock_resp):
        query = Query(text='title:"machine learning" AND year:2023', max_results=5)
        results = [doc async for doc in provider.search(query)]
        assert len(results) == 1
        assert results[0].title == "Attention Is All You Need"
        assert results[0].provider == "openalex"
        assert results[0].external_ids.openalex_id == "W2741809807"


@pytest.mark.asyncio
async def test_pubmed_provider():
    provider = PubMedProvider()
    
    # 1. Mock esearch response
    mock_esearch_resp = MagicMock()
    mock_esearch_resp.status_code = 200
    mock_esearch_resp.json.return_value = {
        "esearchresult": {"idlist": ["12345678"]}
    }

    # 2. Mock efetch XML response
    xml_data = """<?xml version="1.0"?>
    <PubmedArticleSet>
      <PubmedArticle>
        <MedlineCitation>
          <PMID>12345678</PMID>
          <Article>
            <ArticleTitle>CRISPR-Cas9 genome editing in human cells</ArticleTitle>
            <Journal><Title>Nature Biotechnology</Title></Journal>
            <AuthorList>
              <Author><LastName>Doudna</LastName><ForeName>Jennifer A</ForeName></Author>
            </AuthorList>
            <Abstract><AbstractText>Precision gene editing using RNA-guided Cas9.</AbstractText></Abstract>
          </Article>
        </MedlineCitation>
      </PubmedArticle>
    </PubmedArticleSet>
    """
    mock_efetch_resp = MagicMock()
    mock_efetch_resp.status_code = 200
    mock_efetch_resp.content = xml_data.encode("utf-8")

    async def mock_get(url, params=None, **kwargs):
        if "esearch.fcgi" in url:
            return mock_esearch_resp
        return mock_efetch_resp

    with patch.object(provider.client, "get", side_effect=mock_get):
        query = Query(text='title:"machine learning" AND year:2023', max_results=5)
        results = [doc async for doc in provider.search(query)]
        assert len(results) == 1
        assert results[0].title == "CRISPR-Cas9 genome editing in human cells"
        assert results[0].provider == "pubmed"
        assert results[0].external_ids.pubmed_id == "12345678"


@pytest.mark.asyncio
async def test_arxiv_provider():
    provider = ArxivProvider()
    atom_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <entry>
        <id>http://arxiv.org/abs/1706.03762v5</id>
        <published>2017-06-12T00:00:00Z</published>
        <title>Attention Is All You Need</title>
        <summary>The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...</summary>
        <author><name>Ashish Vaswani</name></author>
        <link title="pdf" href="http://arxiv.org/pdf/1706.03762v5" rel="related" type="application/pdf"/>
      </entry>
    </feed>
    """
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = atom_xml
    mock_resp.content = atom_xml.encode("utf-8")

    with patch.object(provider.client, "get", new_callable=AsyncMock, return_value=mock_resp):
        query = Query(text='title:"machine learning"', max_results=5)
        results = [doc async for doc in provider.search(query)]
        assert len(results) == 1
        assert results[0].title == "Attention Is All You Need"
        assert results[0].provider == "arxiv"
        assert results[0].external_ids.arxiv_id == "1706.03762"


@pytest.mark.asyncio
async def test_crossref_provider():
    provider = CrossrefProvider()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "message": {
            "items": [
                {
                    "title": ["Attention Is All You Need"],
                    "DOI": "10.5555/3295222.3295349",
                    "published-print": {"date-parts": [[2017]]},
                    "author": [{"given": "Ashish", "family": "Vaswani"}],
                    "container-title": ["Advances in Neural Information Processing Systems"],
                }
            ]
        }
    }
    with patch.object(provider.client, "get", new_callable=AsyncMock, return_value=mock_resp):
        query = Query(text='title:"machine learning"', max_results=5)
        results = [doc async for doc in provider.search(query)]
        assert len(results) == 1
        assert results[0].title == "Attention Is All You Need"
        assert results[0].provider == "crossref"
        assert results[0].external_ids.doi == "10.5555/3295222.3295349"


@pytest.mark.asyncio
async def test_semanticscholar_mocked():
    provider = SemanticScholarProvider()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
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
    with patch.object(provider.client, "get", new_callable=AsyncMock, return_value=mock_resp):
        query = Query(text="deep residual learning", max_results=1)
        results = [doc async for doc in provider.search(query)]
        assert len(results) == 1
        assert results[0].title == "Deep Residual Learning for Image Recognition"
        assert results[0].external_ids.doi == "10.1109/cvpr.2016.90"
        assert results[0].citations_count == 150000


@pytest.mark.asyncio
async def test_biorxiv_mocked():
    provider = BiorxivProvider()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
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
    with patch.object(provider.client, "get", new_callable=AsyncMock, return_value=mock_resp):
        query = Query(text="crispr genome", max_results=1)
        results = [doc async for doc in provider.search(query)]
        assert len(results) == 1
        assert "CRISPR" in results[0].title
        assert results[0].provider == "biorxiv"
