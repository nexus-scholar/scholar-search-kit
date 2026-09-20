"""Deterministic completeness scoring for representative election.

Scoring formula (0–10 base + provider weight):
  DOI present:          +2
  Abstract >20 chars:   +2
  Venue present:        +1
  Authors non-empty:    +1
  Year present:         +1
  Citations >0:         +1
  Any author has ORCID: +1
  Not retracted:        +1

Provider weights (added to base):
  openalex=5, crossref=4, semanticscholar=3, s2=3,
  arxiv=2, pubmed=2, biorxiv=1, unknown=0

Reference: NEXUS_MASTER_SPECIFICATION.md §3.1.B
"""

from __future__ import annotations

from .models import Document

PROVIDER_WEIGHTS: dict[str, int] = {
    "openalex": 5,
    "crossref": 4,
    "semanticscholar": 3,
    "s2": 3,
    "arxiv": 2,
    "pubmed": 2,
    "biorxiv": 1,
    "unknown": 0,
}


def compute_completeness_score(doc: Document) -> int:
    """Compute a 0–10 completeness score for a document.

    Args:
        doc: Normalized document to score.

    Returns:
        Integer score between 0 and 10.
    """
    score = 0

    # DOI present: +2
    if doc.external_ids.doi:
        score += 2

    # Abstract > 20 chars: +2
    if doc.abstract and len(doc.abstract) > 20:
        score += 2

    # Venue present: +1
    if doc.venue:
        score += 1

    # Authors non-empty: +1
    if doc.authors:
        score += 1

    # Year present: +1
    if doc.year is not None:
        score += 1

    # Citations > 0: +1
    if doc.citations_count is not None and doc.citations_count > 0:
        score += 1

    # Any author has ORCID: +1
    if any(a.orcid for a in doc.authors):
        score += 1

    # Not retracted: +1 (assume not retracted unless explicitly flagged)
    # The Document model doesn't have a retracted flag yet, so this always scores +1.
    score += 1

    return score


def compute_total_score(doc: Document) -> int:
    """Compute total score = completeness score + provider weight.

    Args:
        doc: Normalized document to score.

    Returns:
        Integer total score.
    """
    completeness = compute_completeness_score(doc)
    provider_weight = PROVIDER_WEIGHTS.get(doc.provider.lower(), 0)
    return completeness + provider_weight
