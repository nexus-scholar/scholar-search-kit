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


# ---------------------------------------------------------------------------
# M0.6 (T6.1/T6.2): semantic search param + classifier-grounded topics
# ---------------------------------------------------------------------------


def test_openalex_build_params_semantic_mode_uses_search_semantic_only():
    provider = OpenAlexProvider()
    params = provider._build_params(
        Query(text="deep learning grape disease", semantic=True)
    )
    assert params.get("search.semantic") == "deep learning grape disease"
    assert "search" not in params


def test_openalex_build_params_keyword_mode_keeps_search_unchanged():
    provider = OpenAlexProvider()
    params = provider._build_params(Query(text="deep learning grape disease"))
    assert params.get("search") == "deep learning grape disease"
    assert "search.semantic" not in params


def test_openalex_build_params_semantic_skips_boolean_rewriting():
    provider = OpenAlexProvider()
    params = provider._build_params(
        Query(text='"visual detection" AND edge deployment', semantic=True)
    )
    assert params["search.semantic"] == '"visual detection" AND edge deployment'
    assert "search" not in params


def test_openalex_build_params_semantic_omits_filter_param():
    """OpenAlex `search.semantic` rejects `filter` (HTTP 400, verified live
    2026-09-13); year windows are applied manually in the search loop."""
    provider = OpenAlexProvider()
    semantic = provider._build_params(
        Query(
            text="grape disease detection",
            semantic=True,
            year_min=2019,
            year_max=2026,
        )
    )
    assert "filter" not in semantic
    keyword = provider._build_params(
        Query(text="grape disease detection", year_min=2019, year_max=2026)
    )
    assert "filter" in keyword


def test_openalex_normalize_document_captures_topics():
    provider = OpenAlexProvider()
    raw = {
        "id": "W1",
        "title": "Grape Disease Detection",
        "publication_year": 2024,
        "ids": {"doi": "10.1000/grape", "openalex": "W1"},
        "topics": [
            {"id": "T123", "display_name": "Computer vision", "score": 0.87},
        ],
        "concepts": [{"id": "C1", "display_name": "Legacy concept", "score": 0.99}],
    }
    doc = provider._normalize_document(raw)
    assert doc.topics == [
        {
            "source": "openalex_topics",
            "id": "T123",
            "display_name": "Computer vision",
            "score": 0.87,
        }
    ]


def test_openalex_normalize_document_topics_fall_back_to_concepts():
    provider = OpenAlexProvider()
    raw = {
        "id": "W2",
        "title": "Legacy Work",
        "ids": {"doi": "10.1000/legacy", "openalex": "W2"},
        "concepts": [{"id": "C1", "display_name": "Legacy concept", "score": 0.6}],
    }
    doc = provider._normalize_document(raw)
    assert doc.topics == [
        {
            "source": "openalex_concepts",
            "id": "C1",
            "display_name": "Legacy concept",
            "score": 0.6,
        }
    ]


def test_openalex_normalize_document_topics_none_when_absent():
    provider = OpenAlexProvider()
    raw = {
        "id": "W3",
        "title": "Plain Work",
        "ids": {"doi": "10.1000/plain", "openalex": "W3"},
    }
    doc = provider._normalize_document(raw)
    assert doc.topics is None


# ---------------------------------------------------------------------------
# T6.1 / M0.6: OpenAlex semantic search rejects cursor pagination
# ---------------------------------------------------------------------------


def test_openalex_build_params_semantic_caps_per_page_at_50_and_no_cursor():
    """Semantic mode must NOT set a cursor key and must cap per-page at 50."""
    provider = OpenAlexProvider()
    params = provider._build_params(
        Query(text="deep learning grape disease", semantic=True, max_results=100)
    )
    assert params["search.semantic"] == "deep learning grape disease"
    assert "search" not in params
    assert "cursor" not in params
    assert params["per-page"] == 50  # min(100, 50)


def test_openalex_build_params_semantic_default_max_results():
    """Without max_results, semantic defaults per-page to 50 (the API cap)."""
    provider = OpenAlexProvider()
    params = provider._build_params(Query(text="test", semantic=True))
    assert "cursor" not in params
    assert params["per-page"] == 50  # min(50, 50)


def test_openalex_build_params_semantic_small_max_results():
    """max_results < 50 is respected as-is."""
    provider = OpenAlexProvider()
    params = provider._build_params(Query(text="test", semantic=True, max_results=10))
    assert "cursor" not in params
    assert params["per-page"] == 10


def test_openalex_build_params_keyword_still_uses_cursor_and_correct_per_page():
    """Keyword mode must preserve cursor='*' and per-page=min(max_results or 100, 200)."""
    provider = OpenAlexProvider()
    params = provider._build_params(Query(text="machine learning", max_results=50))
    assert params["cursor"] == "*"
    assert params["per-page"] == 50  # min(50, 200)
    assert "search.semantic" not in params


def test_openalex_build_params_keyword_default_max_results():
    """Keyword without max_results: per-page = min(100, 200) = 100, cursor present."""
    provider = OpenAlexProvider()
    params = provider._build_params(Query(text="machine learning"))
    assert params["cursor"] == "*"
    assert params["per-page"] == 100


def test_openalex_build_params_keyword_large_max_results():
    """Keyword with max_results > 200: per-page capped at 200."""
    provider = OpenAlexProvider()
    params = provider._build_params(Query(text="test", max_results=500))
    assert params["cursor"] == "*"
    assert params["per-page"] == 200


# ---------------------------------------------------------------------------
# Semantic search pagination loop: page-based walk, never cursor
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_openalex_search_semantic_uses_page_based_pagination():
    """Semantic search must walk pages via `page` param, never `cursor`."""
    provider = OpenAlexProvider()
    captured: list[dict] = []

    page_one = {
        "results": [
            {
                "id": "https://openalex.org/W1",
                "title": "Doc One",
                "publication_year": 2024,
                "ids": {"openalex": "W1"},
            }
        ],
        "meta": {"count": 2},
    }
    page_two = {
        "results": [
            {
                "id": "https://openalex.org/W2",
                "title": "Doc Two",
                "publication_year": 2024,
                "ids": {"openalex": "W2"},
            }
        ],
        "meta": {"count": 2},
    }

    async def fake_get(url, params=None, **kwargs):
        captured.append(dict(params))
        page_num = (params or {}).get("page", 1)
        mock = MagicMock()
        mock.status_code = 200
        mock.json.return_value = page_one if page_num == 1 else page_two
        return mock

    with patch.object(provider.client, "get", side_effect=fake_get):
        query = Query(text="grape disease", semantic=True, max_results=10)
        results = [doc async for doc in provider.search(query)]

    assert len(results) == 2
    assert results[0].title == "Doc One"
    assert results[1].title == "Doc Two"

    # First request: no `cursor`, `per-page` = min(10,50) = 10, no `page`
    assert "cursor" not in captured[0]
    assert captured[0]["per-page"] == 10
    assert "page" not in captured[0]

    # Second request: `page` == 2, still no `cursor`
    assert len(captured) == 2
    assert captured[1]["page"] == 2
    assert "cursor" not in captured[1]


@pytest.mark.asyncio
async def test_openalex_search_semantic_stops_at_total():
    """Semantic search stops when count >= meta.count (total)."""
    provider = OpenAlexProvider()
    captured: list[dict] = []

    single_page = {
        "results": [
            {
                "id": f"https://openalex.org/W{i}",
                "title": f"Doc {i}",
                "publication_year": 2024,
                "ids": {"openalex": f"W{i}"},
            }
            for i in range(5)
        ],
        "meta": {"count": 5},
    }

    async def fake_get(url, params=None, **kwargs):
        captured.append(dict(params))
        mock = MagicMock()
        mock.status_code = 200
        mock.json.return_value = single_page
        return mock

    with patch.object(provider.client, "get", side_effect=fake_get):
        # max_results > total to ensure total triggers the break
        query = Query(text="test", semantic=True, max_results=100)
        results = [doc async for doc in provider.search(query)]

    assert len(results) == 5
    # Only one request — total=5, count=5, so break after first page
    assert len(captured) == 1
    assert "cursor" not in captured[0]


@pytest.mark.asyncio
async def test_openalex_search_semantic_stops_at_max_results():
    """Semantic search stops when count >= max_results mid-page."""
    provider = OpenAlexProvider()
    captured: list[dict] = []

    page_resp = {
        "results": [
            {
                "id": f"https://openalex.org/W{i}",
                "title": f"Doc {i}",
                "publication_year": 2024,
                "ids": {"openalex": f"W{i}"},
            }
            for i in range(5)
        ],
        "meta": {"count": 100},  # total > max_results
    }

    async def fake_get(url, params=None, **kwargs):
        captured.append(dict(params))
        mock = MagicMock()
        mock.status_code = 200
        mock.json.return_value = page_resp
        return mock

    with patch.object(provider.client, "get", side_effect=fake_get):
        # max_results=3, so after yielding 3 docs we should return
        query = Query(text="test", semantic=True, max_results=3)
        results = [doc async for doc in provider.search(query)]

    assert len(results) == 3
    # Only one request — max_results reached mid-page (return, not break)
    assert len(captured) == 1


@pytest.mark.asyncio
async def test_openalex_search_keyword_still_uses_cursor():
    """Keyword mode must still walk cursors (untouched baseline)."""
    provider = OpenAlexProvider()
    captured: list[dict] = []

    page_one = {
        "results": [
            {
                "id": "https://openalex.org/W1",
                "title": "Doc One",
                "publication_year": 2024,
                "ids": {"openalex": "W1"},
            }
        ],
        "meta": {"next_cursor": "abc123"},
    }
    page_two = {
        "results": [
            {
                "id": "https://openalex.org/W2",
                "title": "Doc Two",
                "publication_year": 2024,
                "ids": {"openalex": "W2"},
            }
        ],
        "meta": {"next_cursor": None},
    }

    async def fake_get(url, params=None, **kwargs):
        captured.append(dict(params))
        mock = MagicMock()
        mock.status_code = 200
        cursor = (params or {}).get("cursor")
        mock.json.return_value = page_one if cursor == "*" else page_two
        return mock

    with patch.object(provider.client, "get", side_effect=fake_get):
        query = Query(text="machine learning", max_results=10)
        results = [doc async for doc in provider.search(query)]

    assert len(results) == 2
    # First request: cursor = "*"
    assert captured[0]["cursor"] == "*"
    assert "page" not in captured[0]
    # Second request: cursor = "abc123" (from next_cursor)
    assert captured[1]["cursor"] == "abc123"
