# Lesson 2.2: The Normalized Document & Author Model

## 1. Scientific Motivation & Context
Academic documents from different sources arrive in incompatible schemas (OpenAlex JSON, Crossref works JSON, arXiv Atom XML, Semantic Scholar bulk JSON). To enable cross-provider search, deduplication, and export without vendor lock-in, all records must normalize into a single canonical `Document` model while strictly preserving source provenance.

## 2. Reference Architecture Analysis
* **Reference Sources**:
  * `strategy-pipeline/src/slr/core/models.py::Author`
  * `strategy-pipeline/src/slr/core/models.py::Document`
  * `strategy-pipeline/src/slr/core/models.py::SearchResult`
* **Observed Behavior**:
  * `Author`: separates `family_name`, `given_name`, and `orcid`. Computes `full_name` property dynamically.
  * `Document`: required `title`, optional `year`, `provider`, `provider_id`, `external_ids`, `abstract`, `authors`, `venue`, `url`, `language`, `cited_by_count`, `query_id`, `query_text`, `retrieved_at`, `cluster_id`, and `raw_data` (excluded from serialization).
  * `SearchResult`: container wrapping `query`, `documents`, `total_found`, `provider`, `timestamp`, and `errors`.

## 3. Explicit Component Contracts

### 3.1 `Author`
* **Fields**:
  * `family_name`: `str` (required)
  * `given_name`: `Optional[str] = None`
  * `orcid`: `Optional[str] = None` (normalized without URL prefix)
* **Properties**:
  * `full_name -> str`: `f"{given_name} {family_name}"` if `given_name` is present, else `family_name`.

### 3.2 `Document`
#### 🟢 Baseline Implementation Contract (`v0.1.0`)
* **Required Invariants**:
  * `title`: String representing document title.
  * `year`: Optional integer representing publication year.
  * `provider`: String representing the source (defaults to `"unknown"`).
  * `provider_id`: String representing the record in the provider's database (defaults to `""`).
  * `external_ids`: Always an `ExternalIds` instance (default factory).
  * `retrieved_at`: Optional UTC `datetime` (defaults to `None`).
  * `raw_data`: Optional diagnostic dict, excluded from standard exports and JSON serialization.
* **Fields**: `title`, `year`, `provider`, `provider_id`, `external_ids`, `abstract`, `authors`, `venue`, `url`, `query_id`, `retrieved_at`, `cluster_id`, `raw_data`.

#### 🟡 Lesson Milestone Target Contract
* **Extended Invariants**:
  * `title`: Must be non-empty string.
  * `year`: If present, must satisfy $1900 \le \text{year} \le 2100$.
  * `provider`: Restrict to (`"openalex"`, `"crossref"`, `"arxiv"`, `"s2"`, `"memory"`).
  * `provider_id`: Must be non-empty string.
  * `retrieved_at`: Must be explicitly set to a UTC `datetime`.
* **Extended Fields**: `language`, `cited_by_count`, `query_text`.

### 3.3 `SearchResult`
#### 🟡 Lesson Milestone Target Contract
* **Fields**:
  * `query`: `Query`
  * `documents`: `List[Document]`
  * `total_found`: `int` (total matched on provider server, which may exceed `len(documents)`)
  * `provider`: `str`
  * `timestamp`: `datetime` (UTC)
  * `errors`: `List[str]`

## 4. Edge Cases & Counterexamples
| Scenario | Desired Behavior | Failure Mode to Avoid |
| :--- | :--- | :--- |
| Single-name author (e.g. "Plato", "Aristotle") | `Author(family_name="Plato", given_name=None)` | Creating whitespace `" Plato"` or failing required given name |
| Missing publication year | `Document(title="X", year=None)` | Defaulting to `0` or `1970` which corrupts year filtering |
| Timestamp assignment | UTC `datetime.now(timezone.utc)` | Naive local datetimes that break timezone comparisons across servers |

## 5. Verification & Falsifying Tests

```python
from datetime import datetime, timezone
from scholar_search.models import Author, Document, ExternalIds

def test_author_full_name():
    a1 = Author(family_name="Turing", given_name="Alan")
    assert a1.full_name == "Alan Turing"
    
    a2 = Author(family_name="Euclid")
    assert a2.full_name == "Euclid"

def test_document_defaults_and_retrieval():
    doc = Document(title="Computing Machinery and Intelligence", year=1950)
    assert doc.external_ids is not None
    assert doc.authors == []
    assert doc.retrieved_at is None
    
    doc.mark_retrieved()
    assert doc.retrieved_at is not None
    assert doc.retrieved_at.tzinfo == timezone.utc
```

## 6. AI Build Prompt

```text
Implement Author, Document, and SearchResult models in scholar_search.models according to Lesson 2.2 specs.
Ensure Document maintains provenance (query_id, query_text, provider, provider_id, retrieved_at).
Ensure raw_data is excluded during serialization.
Add comprehensive unit tests in tests/test_models.py.
```
