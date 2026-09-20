"""Tests for query_validator module."""

from __future__ import annotations

import asyncio

import pytest

from scholar_search.query_validator import QueryDiagnosticValidator, _clean_doi


class FakeSearchEngine:
    """Mock search engine for testing."""

    def __init__(self, results_map: dict[str, list] | None = None):
        self.results_map = results_map or {}
        self.call_count = 0

    async def search_all(self, query, dedup: bool = True):
        self.call_count += 1
        # The real search_engine.search_all receives a Query object;
        # extract .text for lookup against our map.
        text = query.text if hasattr(query, "text") else query
        return self.results_map.get(text, [])


def _make_doc(doi: str):
    """Create a minimal Document-like object with the structure the validator expects."""

    class _ExtIds:
        def __init__(self, doi_val):
            self.doi = doi_val

    class FakeDoc:
        def __init__(self, doi_val):
            self.external_ids = _ExtIds(doi_val)
            self.title = f"Paper {doi_val}"

    return FakeDoc(doi)


# ---------------------------------------------------------------------------
# validate_and_heal happy-path / error-path tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_validate_perfect_recall_no_healing():
    """All seeds found -> 1 iteration, validated=True."""
    doc1 = _make_doc("10.1000/test1")
    doc2 = _make_doc("10.1000/test2")

    engine = FakeSearchEngine(
        {
            "machine learning": [doc1, doc2],
        }
    )

    validator = QueryDiagnosticValidator(engine)
    result = await validator.validate_and_heal(
        "machine learning",
        ["10.1000/test1", "10.1000/test2"],
    )

    assert result["validated"] is True
    assert result["recall"] == 1.0
    assert len(result["iterations"]) == 1
    assert engine.call_count == 1


@pytest.mark.asyncio
async def test_validate_partial_recall_heals():
    """Some seeds missing -> healing triggered."""
    doc1 = _make_doc("10.1000/test1")
    doc2 = _make_doc("10.1000/test2")

    # First call: only finds test1
    # Second call: finds both (after healing expands query)
    healed_query = "(machine learning) OR (doi:10.1000/test2)"
    engine = FakeSearchEngine(
        {
            "machine learning": [doc1],
            healed_query: [doc1, doc2],
        }
    )

    validator = QueryDiagnosticValidator(engine)
    result = await validator.validate_and_heal(
        "machine learning",
        ["10.1000/test1", "10.1000/test2"],
    )

    assert result["validated"] is True
    assert result["recall"] == 1.0
    assert len(result["iterations"]) == 2


@pytest.mark.asyncio
async def test_validate_max_iterations_respected():
    """Mock never finds seeds -> stops at max_iterations."""
    engine = FakeSearchEngine({"q": []})

    validator = QueryDiagnosticValidator(engine, max_iterations=2)
    result = await validator.validate_and_heal(
        "q",
        ["10.1000/missing"],
    )

    assert result["validated"] is False
    assert len(result["iterations"]) == 2
    assert engine.call_count == 2


@pytest.mark.asyncio
async def test_validate_empty_seeds():
    """Empty golden_seeds -> recall=1.0, validated=True, no search call."""
    engine = FakeSearchEngine({})
    validator = QueryDiagnosticValidator(engine)

    result = await validator.validate_and_heal("q", [])

    assert result["validated"] is True
    assert result["recall"] == 1.0
    assert engine.call_count == 0


@pytest.mark.asyncio
async def test_validate_single_seed_found():
    """Single seed found -> validated immediately."""
    doc = _make_doc("10.1000/a")
    engine = FakeSearchEngine({"q": [doc]})

    validator = QueryDiagnosticValidator(engine)
    result = await validator.validate_and_heal("q", ["10.1000/a"])

    assert result["validated"] is True
    assert result["recall"] == 1.0
    assert len(result["iterations"]) == 1


@pytest.mark.asyncio
async def test_validate_all_seeds_missing_stops_after_max():
    """All seeds missing across all iterations -> validated=False."""
    engine = FakeSearchEngine({"q": [_make_doc("10.9999/unrelated")]})

    validator = QueryDiagnosticValidator(engine, max_iterations=3)
    result = await validator.validate_and_heal("q", ["10.1000/missing"])

    assert result["validated"] is False
    assert result["recall"] == 0.0
    assert len(result["iterations"]) == 3


# ---------------------------------------------------------------------------
# _heal_query tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_heal_query_appends_doi_terms():
    """Verify heuristic expansion format."""
    engine = FakeSearchEngine({})
    validator = QueryDiagnosticValidator(engine)

    healed = await validator._heal_query(
        "machine learning",
        {"10.1000/test1", "10.1000/test2"},
        [],
    )

    assert "(machine learning)" in healed
    assert "doi:10.1000/test1" in healed or "doi:10.1000/test2" in healed
    assert " OR " in healed


@pytest.mark.asyncio
async def test_heal_query_no_missed_seeds_returns_original():
    """When no seeds are missed, the original query is returned unchanged."""
    engine = FakeSearchEngine({})
    validator = QueryDiagnosticValidator(engine)

    healed = await validator._heal_query(
        "machine learning",
        set(),
        [],
    )

    assert healed == "machine learning"


# ---------------------------------------------------------------------------
# _clean_doi tests
# ---------------------------------------------------------------------------


def test_doi_sanitization_various_formats():
    """Test various DOI formats."""
    assert _clean_doi("https://doi.org/10.1000/test") == "10.1000/test"
    assert _clean_doi("http://doi.org/10.1000/test") == "10.1000/test"
    assert _clean_doi("doi:10.1000/test") == "10.1000/test"
    assert _clean_doi("10.1000/test") == "10.1000/test"
    assert _clean_doi("10.1000/test/") == "10.1000/test"
    assert _clean_doi("  10.1000/test  ") == "10.1000/test"


def test_doi_sanitization_case_insensitive_prefix():
    """doi: prefix is case-insensitive."""
    assert _clean_doi("DOI:10.1000/test") == "10.1000/test"
    assert _clean_doi("Doi:10.1000/test") == "10.1000/test"


# ---------------------------------------------------------------------------
# Iteration history structure tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_validate_returns_iteration_history():
    """Each iteration logged with query, count, recall, found_seeds, missed_seeds."""
    doc = _make_doc("10.1000/a")
    engine = FakeSearchEngine({"q": [doc]})

    validator = QueryDiagnosticValidator(engine)
    result = await validator.validate_and_heal("q", ["10.1000/a", "10.1000/b"])

    # Only one iteration because 10.1000/a is found in the single-iteration loop
    # but recall is 0.5 not 1.0, so it heals and tries again.
    # The healed query may or may not find the second seed; either way iterations exist.
    assert len(result["iterations"]) >= 1
    for it in result["iterations"]:
        assert "query" in it
        assert "results_count" in it
        assert "recall" in it
        assert "found_seeds" in it
        assert "missed_seeds" in it


@pytest.mark.asyncio
async def test_validate_result_has_expected_keys():
    """Top-level result dict always has the required keys."""
    engine = FakeSearchEngine({})
    validator = QueryDiagnosticValidator(engine)

    result = await validator.validate_and_heal("q", [])

    for key in (
        "original_query",
        "golden_seeds",
        "iterations",
        "final_query",
        "recall",
        "validated",
    ):
        assert key in result
