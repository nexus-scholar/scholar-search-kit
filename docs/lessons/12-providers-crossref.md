# Lesson 5.3: Ingesting Crossref DOIs & Metadata (`providers/crossref.py`)

## 1. Scientific Motivation & Context
Crossref is the official DOI registration agency for $>140\text{M}$ scholarly records. It represents the primary authority for journal articles, conference proceedings, and book chapters. Ingesting Crossref metadata provides canonical publication years, official DOIs, author ORCIDs, and citation links.

## 2. Reference Architecture Analysis
* **Reference Source**: `strategy-pipeline/src/slr/providers/crossref.py`
* **API Details**:
  * Base URL: `https://api.crossref.org/works`
  * Rate limit: 45–50 req/s polite pool (with `mailto`).
  * Pagination: Deep cursor pagination (`cursor=*`, `next-cursor` in `message`).
  * Page size: `rows=100`.
  * Date parts extraction: Year located in `raw["issued"]["date-parts"][0][0]`.

## 3. Explicit Component Contract

### Class Definition: `CrossrefProvider`
* **Query Parameters (`_translate_query`)**:
  * `query`: Query text.
  * `rows`: `100`.
  * `cursor`: `*` (updated to `response["message"]["next-cursor"]`).
  * `mailto`: Email address to route requests to the Crossref polite pool.
  * `filter`:
    * `from-pub-date:{year_min}-01-01`
    * `until-pub-date:{year_max}-12-31`
    * `type:journal-article,type:proceedings-article,type:posted-content,type:book-chapter,type:monograph`
  * `select`: Field projection for payload reduction.
* **Normalization Logic**:
  * Extracts title from list: `raw["title"][0]`.
  * Extracts year from date-parts: `raw["issued"]["date-parts"][0][0]`.
  * Extracts venue from container title: `raw["container-title"][0]`.

## 4. Verification & Falsifying Tests

```python
from scholar_search.providers.crossref import CrossrefProvider
from scholar_search.core.config import ProviderConfig

def test_crossref_date_parts_extraction():
    provider = CrossrefProvider(ProviderConfig())
    raw_item = {
        "title": ["A Crossref Study"],
        "DOI": "10.1016/j.comp.2023.01",
        "issued": {"date-parts": [[2023, 4, 15]]},
        "container-title": ["Journal of Systems"],
        "author": [{"family": "Shannon", "given": "Claude"}],
    }
    doc = provider._normalize_response(raw_item)
    assert doc is not None
    assert doc.title == "A Crossref Study"
    assert doc.year == 2023
    assert doc.external_ids.doi == "10.1016/j.comp.2023.01"
```

## 5. AI Build Prompt

```text
Implement CrossrefProvider in scholar_search/providers/crossref.py according to Lesson 5.3 specifications.
Support deep cursor pagination, polite pool mailto routing, document type filtering, and date-parts year extraction.
Add mock-based unit tests in tests/test_crossref.py.
```
