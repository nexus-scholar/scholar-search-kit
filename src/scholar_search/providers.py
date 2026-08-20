"""Provider contract and deterministic provider for tests and tutorials."""

from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Protocol

from .models import Document, Query


class SearchProvider(Protocol):
    name: str

    def search(self, query: Query) -> Iterator[Document]:
        ...


class InMemoryProvider:
    """Search provider that filters a fixed document collection."""

    name = "memory"

    def __init__(self, documents: Iterable[Document]) -> None:
        self.documents = list(documents)

    def search(self, query: Query) -> Iterator[Document]:
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


class LocalFileProvider:
    """Provider that yields documents from a local file (RIS or JSONL)."""

    name = "local_file"

    def __init__(self, filepath: str | Path) -> None:
        self.filepath = Path(filepath)

    def search(self, query: Query) -> Iterator[Document]:
        """
        Yields all documents in the file. We intentionally DO NOT filter by query text 
        because the user already ran their manual query in the external database (e.g. Scopus).
        We only apply the strict year bounds and attach the query ID for provenance.
        """
        from .importers import RISImporter, JSONLImporter
        
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