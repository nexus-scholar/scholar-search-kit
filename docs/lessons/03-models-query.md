# Lesson 2.3: Query as a Research Instrument (`Query`)

## 1. Scientific Motivation & Context
In systematic scientific methodology, a search query is a formal research instrument. To make literature reviews reproducible and auditable, a query cannot be a transient string passed ad-hoc to an API. It must be a structured entity with a stable identifier (`Q001`), explicit filter constraints (publication year range, language, max results), and traceable linkage to retrieved records (`Document.query_id`).

---

## 2. Component Contract & Implementation

* **Module**: `scholar_search.models`
* **Dataclass**: `Query`

```python
from dataclasses import dataclass


@dataclass
class Query:
    text: str
    id: str = "Q001"
    year_min: int | None = None
    year_max: int | None = None
    language: str = "en"
    max_results: int | None = None
```

---

## 3. Invariants & Usage Rules

1. **Query Text Verbatim Preservation**: `text` contains the raw Boolean expression or natural search query without premature escaping.
2. **Independent Year Constraints**: Supports open-ended lower bounds (`year_max=2020`), upper bounds (`year_min=2022`), or bounded ranges (`year_min=2020, year_max=2024`).
3. **Traceability**: All documents retrieved using a query carry `Document.query_id == Query.id`.

---

## 4. Verification & Automated Tests

Run with `pytest tests/test_models.py -k "test_query"`:

```python
from scholar_search.models import Query


def test_query_model():
    q = Query(
        id="Q01",
        text='"deep learning" AND robotics',
        year_min=2020,
        year_max=2024,
        max_results=100,
    )
    assert q.id == "Q01"
    assert q.year_min == 2020
    assert q.year_max == 2024
    assert q.max_results == 100
```
