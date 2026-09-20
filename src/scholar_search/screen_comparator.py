"""Screening run comparison for inter-rater reliability analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ScreeningComparisonReport:
    """Report comparing two screening runs."""

    total_compared: int = 0
    agreement_count: int = 0
    agreement_rate: float = 0.0
    transition_matrix: dict[str, dict[str, int]] = field(default_factory=dict)
    discrepancies: list[dict[str, Any]] = field(default_factory=list)
    regression_count: int = 0  # INCLUDE -> EXCLUDE
    progression_count: int = 0  # EXCLUDE -> INCLUDE


def compare_screening_runs(
    run_a: list[dict[str, Any]],
    run_b: list[dict[str, Any]],
    key_fields: list[str] | None = None,
) -> ScreeningComparisonReport:
    """Compare two screening runs and compute agreement metrics.

    Args:
        run_a: First screening run decisions.
        run_b: Second screening run decisions.
        key_fields: Fields to match on (default: ["workspace_id", "doi"]).

    Returns:
        ScreeningComparisonReport with agreement metrics.
    """
    if key_fields is None:
        key_fields = ["workspace_id", "doi"]

    report = ScreeningComparisonReport()

    # Build lookup for run_b
    run_b_map: dict[str, str] = {}
    for decision in run_b:
        key = _make_key(decision, key_fields)
        if key:
            run_b_map[key] = _normalize_decision(decision.get("decision", ""))

    # Compare
    for decision_a in run_a:
        key = _make_key(decision_a, key_fields)
        if not key or key not in run_b_map:
            continue

        dec_a = _normalize_decision(decision_a.get("decision", ""))
        dec_b = run_b_map[key]

        report.total_compared += 1

        # Initialize transition matrix entries
        if dec_a not in report.transition_matrix:
            report.transition_matrix[dec_a] = {}
        if dec_b not in report.transition_matrix[dec_a]:
            report.transition_matrix[dec_a][dec_b] = 0

        report.transition_matrix[dec_a][dec_b] += 1

        if dec_a == dec_b:
            report.agreement_count += 1
        else:
            report.discrepancies.append(
                {
                    "key": key,
                    "run_a": dec_a,
                    "run_b": dec_b,
                }
            )
            # Track regressions and progressions
            if dec_a == "INCLUDE" and dec_b == "EXCLUDE":
                report.regression_count += 1
            elif dec_a == "EXCLUDE" and dec_b == "INCLUDE":
                report.progression_count += 1

    # Compute agreement rate
    if report.total_compared > 0:
        report.agreement_rate = report.agreement_count / report.total_compared

    return report


def _make_key(decision: dict[str, Any], key_fields: list[str]) -> str | None:
    """Create a composite key from decision fields."""
    parts = []
    for field_name in key_fields:
        value = decision.get(field_name)
        if value:
            parts.append(f"{field_name}:{value}")
    return "|".join(parts) if parts else None


def _normalize_decision(decision: str) -> str:
    """Normalize decision to uppercase."""
    return decision.strip().upper() if decision else ""
