# Lesson 5.3: Ingesting Crossref DOIs & Reference Validation (`providers/crossref.py`)

## 1. Scientific Motivation & Context
Crossref is the official DOI registration agency for over 150M published journal articles, conference papers, and monographs. In addition to primary search, Crossref provides bibliographic reference validation (`query.bibliographic`) to verify unformatted citation strings against registered publisher records.

---

## 2. Ingestion & Validation Details

* **Module**: `scholar_search.providers.crossref.CrossrefProvider`
* **Polite Pool**: Automatically attaches `mailto` contact email in request headers.
* **Bibliographic Validation**: Implements `validate_reference(raw_citation_string)` returning match confidence scores and registered metadata.

---

## 3. Verification & Automated Tests

Run with `pytest tests/test_providers.py -k "test_crossref"`:

```python
from scholar_search.providers.crossref import CrossrefProvider
from scholar_search.models import Query


def test_crossref_search():
    provider = CrossrefProvider()
    q = Query(text="deep learning", max_results=5)
    results = list(provider.search(q))
    assert len(results) > 0
    assert results[0].provider == "crossref"
    assert results[0].external_ids.doi is not None
```
