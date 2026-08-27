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
from .http_client import AcademicHttpClient
from .importers import JSONImporter, JSONLImporter, RISImporter
from .models import Author, Document, DocumentCluster, ExternalIds, Query
from .providers import SearchProvider
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
    "ProviderError",
    "Query",
    "RISImporter",
    "RateLimitExceededError",
    "ScholarSearchError",
    "SearchEngine",
    "SearchProvider",
    "VerificationError",
]
