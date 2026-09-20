"""Tests for screen_comparator module."""

import pytest

from scholar_search.screen_comparator import (
    ScreeningComparisonReport,
    compare_screening_runs,
)


@pytest.fixture
def identical_runs():
    """Two identical screening runs."""
    decisions = [
        {"workspace_id": "1", "decision": "INCLUDE"},
        {"workspace_id": "2", "decision": "EXCLUDE"},
        {"workspace_id": "3", "decision": "INCLUDE"},
    ]
    return decisions, decisions.copy()


@pytest.fixture
def run_with_discrepancies():
    """Two runs with known discrepancies."""
    run_a = [
        {"workspace_id": "1", "decision": "INCLUDE"},
        {"workspace_id": "2", "decision": "INCLUDE"},
        {"workspace_id": "3", "decision": "EXCLUDE"},
    ]
    run_b = [
        {"workspace_id": "1", "decision": "INCLUDE"},
        {"workspace_id": "2", "decision": "EXCLUDE"},  # Discrepancy
        {"workspace_id": "3", "decision": "EXCLUDE"},
    ]
    return run_a, run_b


def test_compare_identical_runs(identical_runs):
    """Identical runs should have 100% agreement."""
    run_a, run_b = identical_runs
    report = compare_screening_runs(run_a, run_b)

    assert report.total_compared == 3
    assert report.agreement_rate == 1.0
    assert len(report.discrepancies) == 0


def test_compare_with_discrepancies(run_with_discrepancies):
    """Discrepancies should be tracked correctly."""
    run_a, run_b = run_with_discrepancies
    report = compare_screening_runs(run_a, run_b)

    assert report.total_compared == 3
    assert report.agreement_rate == pytest.approx(2 / 3)
    assert len(report.discrepancies) == 1


def test_regression_count():
    """INCLUDE->EXCLUDE should count as regression."""
    run_a = [{"workspace_id": "1", "decision": "INCLUDE"}]
    run_b = [{"workspace_id": "1", "decision": "EXCLUDE"}]

    report = compare_screening_runs(run_a, run_b)

    assert report.regression_count == 1
    assert report.progression_count == 0


def test_progression_count():
    """EXCLUDE->INCLUDE should count as progression."""
    run_a = [{"workspace_id": "1", "decision": "EXCLUDE"}]
    run_b = [{"workspace_id": "1", "decision": "INCLUDE"}]

    report = compare_screening_runs(run_a, run_b)

    assert report.progression_count == 1
    assert report.regression_count == 0


def test_case_normalization():
    """Case differences should not cause false discrepancies."""
    run_a = [{"workspace_id": "1", "decision": "include"}]
    run_b = [{"workspace_id": "1", "decision": "INCLUDE"}]

    report = compare_screening_runs(run_a, run_b)

    assert report.agreement_rate == 1.0


def test_empty_intersection():
    """No common keys should result in 0 compared."""
    run_a = [{"workspace_id": "1", "decision": "INCLUDE"}]
    run_b = [{"workspace_id": "999", "decision": "INCLUDE"}]

    report = compare_screening_runs(run_a, run_b)

    assert report.total_compared == 0
    assert report.agreement_rate == 0.0


def test_fallback_key_doi():
    """Should match by DOI when workspace_id absent."""
    run_a = [{"doi": "10.1234/test", "decision": "INCLUDE"}]
    run_b = [{"doi": "10.1234/test", "decision": "EXCLUDE"}]

    report = compare_screening_runs(run_a, run_b)

    assert report.total_compared == 1
    assert len(report.discrepancies) == 1
