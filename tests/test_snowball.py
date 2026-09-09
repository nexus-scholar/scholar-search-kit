from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from scholar_search.models import Document, ExternalIds
from scholar_search.snowball import (
    ChainingResult,
    CitationChainer,
    CitationEdge,
    _canonical_keys,
    _normalize_doc_id,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _async_gen(items):
    for item in items:
        yield item


def _doc(title: str, provider_id: str, year: int | None = None, **kw) -> Document:
    return Document(
        title=title,
        year=year,
        provider=kw.get("provider", "openalex"),
        provider_id=provider_id,
        external_ids=kw.get("external_ids", ExternalIds()),
    )


def _mock_engine(provider_mock) -> MagicMock:
    engine = MagicMock()
    engine.providers = [provider_mock]
    return engine


# ---------------------------------------------------------------------------
# Unit: _normalize_doc_id
# ---------------------------------------------------------------------------

class TestNormalizeDocId:
    def test_openalex_full_url(self):
        assert _normalize_doc_id("https://openalex.org/W2741809807") == "W2741809807"

    def test_openalex_short(self):
        assert _normalize_doc_id("W2741809807") == "W2741809807"

    def test_openalex_api_url(self):
        assert _normalize_doc_id("https://api.openalex.org/works/W123") == "W123"

    def test_non_openalex_passthrough(self):
        assert _normalize_doc_id("10.1234/abc") == "10.1234/abc"


# ---------------------------------------------------------------------------
# Unit: _canonical_keys
# ---------------------------------------------------------------------------

class TestCanonicalKeys:
    def test_doi_and_provider_id(self):
        doc = _doc(
            "Test",
            "https://openalex.org/W123",
            external_ids=ExternalIds(doi="10.1000/test"),
        )
        keys = _canonical_keys(doc)
        assert "https://openalex.org/W123" in keys
        assert "W123" in keys
        assert "10.1000/test" in keys

    def test_fallback_key(self):
        doc = _doc("Some Paper", "")
        keys = _canonical_keys(doc)
        assert any(k.startswith("fallback:") for k in keys)


# ---------------------------------------------------------------------------
# Unit: CitationEdge / ChainingResult dataclasses
# ---------------------------------------------------------------------------

class TestDataclasses:
    def test_citation_edge_fields(self):
        e = CitationEdge(
            source_id="A", target_id="B", direction="forward", hop=1, provider="openalex"
        )
        assert e.source_id == "A"
        assert e.hop == 1

    def test_chaining_result_defaults(self):
        result = ChainingResult()
        assert result.documents == []
        assert result.edges == []
        assert result.visited_ids == set()
        assert result.stats == {}


# ---------------------------------------------------------------------------
# Integration: CitationChainer with mocked providers
# ---------------------------------------------------------------------------

class TestCitationChainer:
    @pytest.mark.asyncio
    async def test_single_hop_backward(self):
        ref1 = _doc("Reference 1", "WRef1", year=2020)
        ref2 = _doc("Reference 2", "WRef2", year=2021)

        mock_p = MagicMock()
        mock_p.name = "openalex"
        mock_p.get_references = MagicMock(side_effect=lambda _: _async_gen([ref1, ref2]))
        mock_p.get_citations = MagicMock(side_effect=lambda _: _async_gen([]))

        chainer = CitationChainer(engine=_mock_engine(mock_p))
        result = await chainer.chain(
            seeds=["WSeed1"], provider="openalex", directions=["backward"]
        )

        assert result.stats["total_unique"] == 2
        assert len(result.edges) == 2
        assert all(e.hop == 1 for e in result.edges)
        assert all(e.direction == "backward" for e in result.edges)

    @pytest.mark.asyncio
    async def test_multi_hop_depth_2(self):
        ref1 = _doc("Ref depth 1", "WRef1", year=2020)
        ref2 = _doc("Ref depth 2", "WRef2", year=2021)

        async def mock_refs(doc_id):
            if doc_id == "WSeed1":
                yield ref1
            elif doc_id == "WRef1":
                yield ref2

        mock_p = MagicMock()
        mock_p.name = "openalex"
        mock_p.get_references = mock_refs
        mock_p.get_citations = MagicMock(side_effect=lambda _: _async_gen([]))

        chainer = CitationChainer(engine=_mock_engine(mock_p))
        result = await chainer.chain(
            seeds=["WSeed1"], provider="openalex", directions=["backward"], max_depth=2
        )

        assert result.stats["total_unique"] == 2
        hops = {e.hop for e in result.edges}
        assert 1 in hops and 2 in hops

    @pytest.mark.asyncio
    async def test_cycle_prevention(self):
        seed = _doc("Seed", "WSeed1")
        a = _doc("Paper A", "WA1")

        async def mock_refs(doc_id):
            if doc_id == "WSeed1":
                yield a
            elif doc_id == "WA1":
                yield seed

        mock_p = MagicMock()
        mock_p.name = "openalex"
        mock_p.get_references = mock_refs
        mock_p.get_citations = MagicMock(side_effect=lambda _: _async_gen([]))

        chainer = CitationChainer(engine=_mock_engine(mock_p))
        result = await chainer.chain(
            seeds=["WSeed1"], provider="openalex", max_depth=3
        )

        titles = [d.title for d in result.documents]
        assert "Seed" not in titles
        assert "Paper A" in titles

    @pytest.mark.asyncio
    async def test_max_per_node_cap(self):
        docs = [_doc(f"Doc {i}", f"WDoc{i}") for i in range(10)]

        mock_p = MagicMock()
        mock_p.name = "openalex"
        mock_p.get_references = MagicMock(side_effect=lambda _: _async_gen(docs))
        mock_p.get_citations = MagicMock(side_effect=lambda _: _async_gen([]))

        chainer = CitationChainer(engine=_mock_engine(mock_p))
        result = await chainer.chain(
            seeds=["WSeed1"], provider="openalex", max_per_node=3
        )

        assert result.stats["total_raw"] <= 3
        assert result.stats["total_unique"] <= 3

    @pytest.mark.asyncio
    async def test_max_total_cap(self):
        docs = [_doc(f"Doc {i}", f"WDoc{i}") for i in range(20)]

        mock_p = MagicMock()
        mock_p.name = "openalex"
        mock_p.get_references = MagicMock(side_effect=lambda _: _async_gen(docs))
        mock_p.get_citations = MagicMock(side_effect=lambda _: _async_gen([]))

        chainer = CitationChainer(engine=_mock_engine(mock_p))
        result = await chainer.chain(
            seeds=["WSeed1"], provider="openalex", max_total=5
        )

        assert result.stats["total_raw"] == 5
        assert result.stats["total_unique"] <= 5

    @pytest.mark.asyncio
    async def test_year_filter(self):
        ref_old = _doc("Old paper", "WOld", year=2000)
        ref_new = _doc("New paper", "WNew", year=2022)

        mock_p = MagicMock()
        mock_p.name = "openalex"
        mock_p.get_references = MagicMock(side_effect=lambda _: _async_gen([ref_old, ref_new]))
        mock_p.get_citations = MagicMock(side_effect=lambda _: _async_gen([]))

        chainer = CitationChainer(engine=_mock_engine(mock_p))
        result = await chainer.chain(
            seeds=["WSeed1"], provider="openalex", year_min=2015
        )

        titles = [d.title for d in result.documents]
        assert "Old paper" not in titles
        assert "New paper" in titles

    @pytest.mark.asyncio
    async def test_empty_seeds(self):
        mock_p = MagicMock()
        mock_p.name = "openalex"

        chainer = CitationChainer(engine=_mock_engine(mock_p))
        result = await chainer.chain(seeds=[], provider="openalex")

        assert result.documents == []
        assert result.edges == []
        assert result.stats["total_unique"] == 0

    @pytest.mark.asyncio
    async def test_both_directions(self):
        ref_b = _doc("Backward ref", "WBack")
        ref_f = _doc("Forward cit", "WCit")

        mock_p = MagicMock()
        mock_p.name = "openalex"
        mock_p.get_references = MagicMock(side_effect=lambda _: _async_gen([ref_b]))
        mock_p.get_citations = MagicMock(side_effect=lambda _: _async_gen([ref_f]))

        chainer = CitationChainer(engine=_mock_engine(mock_p))
        result = await chainer.chain(
            seeds=["WSeed1"],
            provider="openalex",
            directions=["forward", "backward"],
        )

        dirs = {e.direction for e in result.edges}
        assert "forward" in dirs
        assert "backward" in dirs

    @pytest.mark.asyncio
    async def test_progress_callback_invoked(self):
        ref = _doc("Ref", "WRef1")

        mock_p = MagicMock()
        mock_p.name = "openalex"
        mock_p.get_references = MagicMock(side_effect=lambda _: _async_gen([ref]))
        mock_p.get_citations = MagicMock(side_effect=lambda _: _async_gen([]))

        cb = MagicMock()
        chainer = CitationChainer(engine=_mock_engine(mock_p))
        await chainer.chain(seeds=["WSeed1"], provider="openalex", progress_callback=cb)

        cb.assert_called()

    @pytest.mark.asyncio
    async def test_unknown_provider_raises(self):
        mock_p = MagicMock()
        mock_p.name = "openalex"

        chainer = CitationChainer(engine=_mock_engine(mock_p))
        with pytest.raises(ValueError, match="Provider 'arxiv'"):
            await chainer.chain(seeds=["WSeed1"], provider="arxiv")


# ---------------------------------------------------------------------------
# CLI integration: chain command
# ---------------------------------------------------------------------------

class TestCLIChain:
    def test_cli_chain_help(self):
        from scholar_search.cli import app
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(app, ["chain", "--help"])
        assert result.exit_code == 0
        assert "Multi-hop" in result.stdout

    def test_cli_chain_basic(self, tmp_path: Path):
        from scholar_search.cli import app
        from typer.testing import CliRunner

        dummy = _doc("Chained Paper", "WChain1", year=2021)
        mock_result = ChainingResult(
            documents=[dummy],
            edges=[
                CitationEdge(
                    source_id="WSeed",
                    target_id="WChain1",
                    direction="backward",
                    hop=1,
                    provider="openalex",
                )
            ],
            stats={"directions": ["backward"], "max_depth": 1},
        )

        output_file = tmp_path / "chain.json"
        edges_file = tmp_path / "edges.json"

        with patch("scholar_search.cli.SearchEngine") as MockEngine:
            MockEngine.return_value.close = AsyncMock()
            with patch("scholar_search.snowball.CitationChainer") as MockChainer:
                instance = AsyncMock()
                instance.chain.return_value = mock_result
                MockChainer.return_value = instance

                runner = CliRunner()
                result = runner.invoke(
                    app,
                    [
                        "chain",
                        "WSeed",
                        "--depth",
                        "1",
                        "-o",
                        str(output_file),
                        "--edges-output",
                        str(edges_file),
                    ],
                )

                assert result.exit_code == 0
                assert "Chained Paper" in result.stdout
                assert output_file.exists()
                assert edges_file.exists()