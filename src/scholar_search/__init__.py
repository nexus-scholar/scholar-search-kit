"""Scholarly search, deduplication, verification, and export toolkit."""

from .dedup import Deduplicator
from .engine import SearchEngine
from .exceptions import (
    InvalidQueryError,
    ProviderError,
    RateLimitExceededError,
    ScholarSearchError,
    VerificationError,
)
from .export import Exporter
from .protocol_adapter import compile_protocol_search
from .providers import SearchProvider
from .screening import (
    PrismaFlowReport,
    ScreeningDecision,
    batch_partition,
    evaluate_heuristic_screening,
    generate_batch_screening_prompt,
    partition_screening_results,
)
from .verifier import DocumentVerifier

__all__ = [
    "AcademicHttpClient",
    "Author",
    "Deduplicator",
    "Document",
    "DocumentCluster",
    "DocumentVerifier",
    "Exporter",
    "ExternalIds",
    "InvalidQueryError",
    "JSONImporter",
    "JSONLImporter",
    "PrismaFlowReport",
    "ProviderError",
    "Query",
    "RISImporter",
    "RateLimitExceededError",
    "ScholarSearchError",
    "ScreeningDecision",
    "SearchEngine",
    "SearchProvider",
    "VerificationError",
    "batch_partition",
    "compile_protocol_search",
    "evaluate_heuristic_screening",
    "generate_batch_screening_prompt",
    "partition_screening_results",
]
