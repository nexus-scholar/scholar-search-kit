# Lesson 2.3: Query as a Research Instrument (`Query`)

## 1. Scientific Motivation & Context
In scientific methodology, a search query is a formal research instrument. To make searches reproducible and auditable, the query cannot be a transient string passed to an API. It must be a structured, immutable entity with a stable identifier, explicit filter constraints (year range, language, max results), and metadata connecting it to research questions or systematic review protocols.

## 2. Reference Architecture Analysis
* **Reference Source**: `strategy-pipeline/src/slr/core/models.py::Query`
* **Observed Behavior**:
  * Pydantic model with default ID generator (`Q{hash:05d}`).
  * Fields for `text`, `year_min`, `year_max`, `language`, `max_results`, and `metadata: Dict[str, Any]`.
  * Provider-independent representation.

## 3. Explicit Component Contract

### Class Definition: `Query`
* **Module**: `scholar_search.models`
* **Attributes**:
  * `id`: `str = "Q001"` — Stable query identifier.
  * `text`: `str` — Query text or Boolean expression (e.g. `"machine learning" AND agriculture`).
  * `year_min`: `Optional[int] = None` — Minimum publication year bound (inclusive).
  * `year_max`: `Optional[int] = None` — Maximum publication year bound (inclusive).
  * `language`: `str = "en"` — ISO 639-1 language code.
  * `max_results`: `Optional[int] = None` — Maximum result count constraint.
  * `metadata`: `Dict[str, Any] = field(default_factory=dict)` — Research context metadata.

### Invariants & Validation Rules
1. **Query Text Integrity**: `text` is preserved verbatim without premature provider-specific escaping.
2. **Year Range Validity**: If both `year_min` and `year_max` are present, `year_min <= year_max` must hold.
3. **Identifier Stability**: Query IDs must be deterministic or explicitly assigned to ensure traceability in exported results (`Document.query_id == Query.id`).

## 4. Edge Cases & Counterexamples
| Scenario | Desired Behavior | Failure Mode to Avoid |
| :--- | :--- | :--- |
| Open-ended lower bound | `Query(text="AI", year_max=2020)` | Generating negative or invalid year queries |
| Open-ended upper bound | `Query(text="AI", year_min=2023)` | Assuming current year as fixed constant |
| Multi-word Boolean string | Preserved as exact raw string | Prematurely stripping quotes or uppercase `AND`/`OR` |

## 5. Verification & Falsifying Tests

```python
import pytest
from scholar_search.models import Query

def test_query_creation_and_bounds():
    q = Query(
        id="Q01",
        text='"deep learning" AND robotics',
        year_min=2020,
        year_max=2024,
        max_results=100
    )
    assert q.id == "Q01"
    assert q.year_min == 2020
    assert q.year_max == 2024
    assert q.max_results == 100
```

## 6. AI Build Prompt

```text
Implement the Query model in scholar_search.models according to Lesson 2.3 specifications.
Ensure Query supports stable IDs, independent year bounds, language codes, result limits, and metadata.
Add unit tests in tests/test_models.py.
```
