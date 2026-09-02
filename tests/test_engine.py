from unittest.mock import MagicMock
import pytest

from scholar_search.engine import SearchEngine
from scholar_search.models import Document, ExternalIds, Query


async def _async_gen(items):
    for item in items:
        yield item


@pytest.mark.asyncio
async def test_search_engine_federation_and_dedup():
    doc1 = Document(
        title="Attention Is All You Need",
        year=2017,
        provider="openalex",
        external_ids=ExternalIds(doi="10.5555/3295222.3295349"),
    )
    doc2 = Document(
        title="Attention Is All You Need",
        year=2017,
        provider="arxiv",
        external_ids=ExternalIds(doi="10.5555/3295222.3295349", arxiv_id="1706.03762"),
        abstract="The dominant sequence transduction models...",
    )
    doc3 = Document(
        title="BERT: Pre-training of Deep Bidirectional Transformers",
        year=2018,
        provider="arxiv",
        external_ids=ExternalIds(arxiv_id="1810.04805"),
    )

    mock_p1 = MagicMock()
    mock_p1.name = "openalex"
    mock_p1.search = MagicMock(side_effect=lambda q: _async_gen([doc1]))

    mock_p2 = MagicMock()
    mock_p2.name = "arxiv"
    mock_p2.search = MagicMock(side_effect=lambda q: _async_gen([doc2, doc3]))

    engine = SearchEngine(providers=[mock_p1, mock_p2])
    results = await engine.search_all(Query(text="transformer"), dedup=True)

    # 3 raw docs should be deduplicated to 2 unique docs
    assert len(results) == 2
    # Metadata merging should have attached the abstract and arxiv_id to the Attention paper
    attention_paper = next(d for d in results if "Attention" in d.title)
    assert attention_paper.external_ids.arxiv_id == "1706.03762"
    assert attention_paper.abstract == "The dominant sequence transduction models..."


@pytest.mark.asyncio
async def test_search_engine_snowball():
    mock_p1 = MagicMock()
    mock_p1.name = "openalex"
    mock_p1.get_citations = MagicMock(
        side_effect=lambda doc_id: _async_gen([Document(title="Citing Paper", provider="openalex")])
    )
    mock_p1.get_references = MagicMock(
        side_effect=lambda doc_id: _async_gen([Document(title="Referenced Paper", provider="openalex")])
    )

    engine = SearchEngine(providers=[mock_p1])
    citations = await engine.snowball_forward("W123", "openalex")
    references = await engine.snowball_backward("W123", "openalex")

    assert len(citations) == 1
    assert citations[0].title == "Citing Paper"
    assert len(references) == 1
    assert references[0].title == "Referenced Paper"

