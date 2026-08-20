# Lesson 5.5: Ingesting Semantic Scholar Bulk Search (`providers/s2.py`)

## 1. Scientific Motivation & Context
Semantic Scholar (Allen Institute for AI) provides rich AI-curated academic graph metadata, citation counts, influential citations, and fields of study. Its high-throughput bulk search endpoint allows retrieving large result sets rapidly using continuation tokens, but requires rewriting human Boolean syntax into bulk query symbols (`+`, `|`, `-`).

## 2. Reference Architecture Analysis
* **Reference Source**: `strategy-pipeline/src/slr/providers/s2.py`
* **API Details**:
  * Base URL: `https://api.semanticscholar.org/graph/v1/paper/search/bulk`
  * Rate limit: 100 requests/sec on bulk endpoint.
  * Pagination: Continuation `token` received in response.
  * Fields requested: `paperId,corpusId,title,abstract,year,authors,venue,citationCount,isOpenAccess,externalIds,url`.

## 3. Explicit Component Contract

### Class Definition: `SemanticScholarProvider`
* **Bulk Query Syntax Rewriting (`_to_bulk_query`)**:
  * `AND` $\rightarrow$ `+`
  * `OR` $\rightarrow$ `|`
  * `NOT <term>` $\rightarrow$ `-<term>` (prefix operator)
  * Space-separated terms without operators are treated as all-required.
* **Pagination Loop (`search`)**:
  * If `token` exists, sets `params["token"] = token`.
  * Loops until `response.get("data")` is empty or no continuation `token` is returned.
* **Normalization Logic (`_normalize_response`)**:
  * Extracts `paperId` as `provider_id` and `s2_id`.
  * Extracts `externalIds.DOI`, `externalIds.ArXiv`, `externalIds.PubMed`.
  * Extracts citation counts and open access status.

## 4. Verification & Falsifying Tests

```python
from scholar_search.providers.s2 import _to_bulk_query, SemanticScholarProvider
from scholar_search.core.config import ProviderConfig

def test_s2_bulk_query_rewriting():
    assert _to_bulk_query("machine learning AND robotics") == "machine learning + robotics"
    assert _to_bulk_query("vision OR audio") == "vision | audio"
    assert _to_bulk_query("deep learning NOT reinforcement") == "deep learning -reinforcement"

def test_s2_normalization():
    provider = SemanticScholarProvider(ProviderConfig())
    raw = {
        "paperId": "s2_12345",
        "title": "A Study in AI",
        "year": 2022,
        "externalIds": {"DOI": "10.1/abc", "ArXiv": "2201.0001"},
        "authors": [{"name": "Geoffrey Hinton"}]
    }
    doc = provider._normalize_response(raw)
    assert doc is not None
    assert doc.provider_id == "s2_12345"
    assert doc.external_ids.doi == "10.1/abc"
    assert doc.external_ids.arxiv_id == "2201.0001"
```

## 5. AI Build Prompt

```text
Implement SemanticScholarProvider and _to_bulk_query in scholar_search/providers/s2.py following Lesson 5.5.
Support bulk search token pagination, Boolean symbol rewriting (+, |, -), fields projection, and external ID extraction.
Add unit tests in tests/test_s2.py.
```
