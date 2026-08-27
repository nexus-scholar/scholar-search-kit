# Lesson 5.1: The Provider Protocol & Multi-Provider Engine (`providers/base.py` & `engine.py`)

## 1. Scientific Motivation & Context
No single academic index has complete coverage of global scholarly literature. Biomedical literature lives in PubMed, computer science preprints in arXiv, open-access metadata in OpenAlex, published DOI records in Crossref, and AI citation graphs in Semantic Scholar.

To achieve exhaustive literature discovery, we define a polymorphic `SearchProvider` protocol orchestrated by a federated `SearchEngine`.

---

## 2. Component Contract & Implementation

* **Module**: `scholar_search.providers.base` & `scholar_search.engine`

```python
from typing import Protocol, Iterator
from scholar_search.models import Query, Document


class SearchProvider(Protocol):
    name: str

    def search(self, query: Query) -> Iterator[Document]:
        """Execute search and yield normalized Document objects."""
        ...
```

* **Federated `SearchEngine`**:
  - Distributes the `Query` across selected providers (`openalex`, `crossref`, `pubmed`, `arxiv`, `semanticscholar`, `biorxiv`).
  - Merges and deduplicates results into `DocumentCluster` representations.
  - Supports backward and forward citation snowballing.

---

## 3. Verification & Automated Tests

Run with `pytest tests/test_engine.py`:

```python
from scholar_search.engine import SearchEngine
from scholar_search.models import Query


def test_search_engine_federation():
    engine = SearchEngine(providers=["openalex", "crossref"])
    q = Query(text="quantum computing", max_results=10)
    results = engine.search(q)
    assert len(results) > 0
```
