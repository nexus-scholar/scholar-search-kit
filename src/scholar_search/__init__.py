"""Small, deterministic scholarly search toolkit used by the harness tutorial."""

from .dedup import Deduplicator
from .models import Author, Document, ExternalIds, Query
from .providers import InMemoryProvider, SearchProvider

__all__ = [
    "Author",
    "Deduplicator",
    "Document",
    "ExternalIds",
    "InMemoryProvider",
    "Query",
    "SearchProvider",
]