# Lesson 5.5: Ingesting Semantic Scholar Bulk Search (`providers/semanticscholar.py`)

## 1. Scientific Motivation & Context
Semantic Scholar (Allen Institute for AI) provides rich citation graphs, influential citations, citation intents (`methodology`, `background`), and TLDR summaries. Its bulk search and graph endpoints enable deep bibliometric exploration.

---

## 2. Ingestion & Graph Traversal Details

* **Module**: `scholar_search.providers.semanticscholar.SemanticScholarProvider`
* **Bulk Search**: Uses `https://api.semanticscholar.org/graph/v1/paper/search/bulk` with continuation `token` parameters.
* **Citation Snowballing**:
  - `get_citations(paper_id)`: Traverses `/citations` endpoint.
  - `get_references(paper_id)`: Traverses `/references` endpoint.
* **Metadata Extraction**: Captures `citations_count`, `references_count`, `citation_intents`, `tldr`, and S2 Corpus IDs.

---

## 3. Verification & Automated Tests

Run with `pytest tests/test_providers.py -k "test_semanticscholar"`:

```python
from scholar_search.providers.semanticscholar import SemanticScholarProvider
from scholar_search.models import Query


def test_semanticscholar_search():
    provider = SemanticScholarProvider()
    q = Query(text="generative adversarial networks", max_results=5)
    results = list(provider.search(q))
    assert len(results) > 0
    assert results[0].provider == "semanticscholar"
```
