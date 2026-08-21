"""Scholarly search, deduplication, verification, and export toolkit."""

from .models import Author, Document, DocumentCluster, ExternalIds, Query
from .dedup import Deduplicator
from .engine import SearchEngine
from .export import Exporter
from .importers import RISImporter, JSONImporter, JSONLImporter
from .http_client import AcademicHttpClient
from .verifier import DocumentVerifier
from .providers import SearchProvider
from .exceptions import ScholarSearchError, ProviderError, RateLimitExceededError, InvalidQueryError, VerificationError

__all__ = [
    "Author",
    "Document",
    "DocumentCluster",
    "ExternalIds",
    "Query",
    "Deduplicator",
    "SearchEngine",
    "Exporter",
    "RISImporter",
    "JSONImporter",
    "JSONLImporter",
    "AcademicHttpClient",
    "DocumentVerifier",
    "SearchProvider",
    "ScholarSearchError",
    "ProviderError",
    "RateLimitExceededError",
    "InvalidQueryError",
    "VerificationError"
]