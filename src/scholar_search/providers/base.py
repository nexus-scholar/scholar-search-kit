"""Provider contract and base implementations."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Iterable, Iterator
from pathlib import Path
from typing import Protocol

from ..http_client import AcademicHttpClient
from ..models import Document, Query


class SearchProvider(Protocol):
    """Protocol that all search providers must implement."""

    name: str

    async def search(self, query: Query) -> AsyncIterator[Document]: ...

    async def get_citations(self, document_id: str) -> AsyncIterator[Document]:
        """Forward snowballing: find papers that cite this document."""
        ...
        yield

    async def get_references(self, document_id: str) -> AsyncIterator[Document]:
        """Backward snowballing: find papers that this document cites."""
        ...
        yield


class BaseAPIProvider(ABC):
    """Abstract base class for live API providers."""

    def __init__(self, name: str, rate_limit: float):
        self.name = name
        self.client = AcademicHttpClient(name=name, rate_limit=rate_limit)

    @abstractmethod
    async def search(self, query: Query) -> AsyncIterator[Document]:
        pass
        yield

    async def get_citations(self, document_id: str) -> AsyncIterator[Document]:
        """Default implementation yields nothing. Override if supported."""
        if False:
            yield None

    async def get_references(self, document_id: str) -> AsyncIterator[Document]:
        """Default implementation yields nothing. Override if supported."""
        if False:
            yield None


# Legacy Local Providers (for tutorials and offline usage)


class InMemoryProvider:
    """Search provider that filters a fixed document collection."""

    name = "memory"

    def __init__(self, documents: Iterable[Document]) -> None:
        self.documents = list(documents)

    async def search(self, query: Query) -> AsyncIterator[Document]:
        terms = [term.lower() for term in query.text.split() if term]
        count = 0
        for document in self.documents:
            haystack = f"{document.title} {document.abstract or ''}".lower()
            if terms and not all(term in haystack for term in terms):
                continue
            if query.year_min is not None and (document.year or 0) < query.year_min:
                continue
            if query.year_max is not None and (document.year or 9999) > query.year_max:
                continue
            document.query_id = query.id
            document.mark_retrieved()
            yield document
            count += 1
            if query.max_results is not None and count >= query.max_results:
                return

    async def get_citations(self, document_id: str) -> AsyncIterator[Document]:
        if False:
            yield None

    async def get_references(self, document_id: str) -> AsyncIterator[Document]:
        if False:
            yield None


class LocalFileProvider:
    """Provider that yields documents from a local file (RIS or JSONL)."""

    name = "local_file"

    def __init__(self, filepath: str | Path) -> None:
        self.filepath = Path(filepath)

    async def search(self, query: Query) -> AsyncIterator[Document]:
        from ..importers import JSONLImporter, RISImporter

        if self.filepath.suffix.lower() == ".ris":
            importer = RISImporter()
        else:
            importer = JSONLImporter()

        for document in importer.parse(self.filepath):
            if query.year_min is not None and (document.year or 0) < query.year_min:
                continue
            if query.year_max is not None and (document.year or 9999) > query.year_max:
                continue

            document.query_id = query.id
            document.mark_retrieved()
            yield document

    async def get_citations(self, document_id: str) -> AsyncIterator[Document]:
        if False:
            yield None

    async def get_references(self, document_id: str) -> AsyncIterator[Document]:
        if False:
            yield None
