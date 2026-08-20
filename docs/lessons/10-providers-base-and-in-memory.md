# Lesson 5.1: The Provider Protocol & In-Memory Engine (`providers/base.py`)

## 1. Scientific Motivation & Context
Testing literature search workflows against live APIs creates non-deterministic tests, triggers rate limits, requires API credentials, and fails during network downtime. By establishing an abstract `BaseProvider` contract and a deterministic `InMemoryProvider`, complete research pipelines can be tested, benchmarked, and demonstrated entirely offline without external dependencies.

## 2. Reference Architecture Analysis
* **Reference Source**: `strategy-pipeline/src/slr/providers/base.py`
* **Components**:
  * `BaseProvider(ABC)`: Abstract class managing rate limiter initialization, `_make_request()` with retries, and abstract methods `search()`, `_translate_query()`, `_normalize_response()`.
  * `ProviderRegistry`: Central registration and discovery engine.
  * `InMemoryProvider`: In-memory collection filtering engine.

## 3. Explicit Component Contract

### 3.1 `SearchProvider` Protocol / `BaseProvider`
* **Methods**:
  * `search(query: Query) -> Iterator[Document]`: Main entry point yielding normalized documents.
  * `_translate_query(query: Query) -> Dict[str, Any]`: Converts `Query` to provider API params.
  * `_normalize_response(raw: Dict[str, Any]) -> Optional[Document]`: Normalizes provider payload.
  * `_make_request(url: str, params: Dict, headers: Dict) -> Dict[str, Any]`: Executes HTTP request with TokenBucket waiting and retry logic.

### 3.2 `InMemoryProvider`
* **Behavior**:
  * Initializes with `Iterable[Document]`.
  * Filters in-memory documents against:
    1. Case-insensitive term search across `title` and `abstract`.
    2. Lower and upper publication year bounds (`year_min`, `year_max`).
    3. Maximum results count (`max_results`).
  * Attaches `query_id` and calls `doc.mark_retrieved()` on each returned record.

## 4. Verification & Falsifying Tests

```python
from scholar_search.models import Document, Query
from scholar_search.providers import InMemoryProvider

def test_in_memory_provider_deterministic_filtering():
    corpus = [
        Document("Neural Networks in Medicine", year=2021, abstract="Clinical study"),
        Document("Neural Networks in Finance", year=2023, abstract="Market analysis"),
        Document("Quantum Computing", year=2022, abstract="Physics review"),
    ]
    provider = InMemoryProvider(corpus)
    
    q = Query(id="Q99", text="neural medicine", year_min=2020)
    results = list(provider.search(q))
    
    assert len(results) == 1
    assert results[0].title == "Neural Networks in Medicine"
    assert results[0].query_id == "Q99"
    assert results[0].retrieved_at is not None
```

## 5. AI Build Prompt

```text
Implement BaseProvider, ProviderRegistry, and InMemoryProvider in scholar_search/providers/base.py and providers.py following Lesson 5.1.
Ensure InMemoryProvider filters on terms, years, and max_results deterministically and sets query provenance.
Add unit tests in tests/test_providers.py.
```
