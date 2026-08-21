# Episode 12: The SearchProvider Protocol

**Objective:** Define a clean `SearchProvider` interface enabling pluggable academic database integrations.

## Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | The contract that connects our engine to the world's academic repositories. | *Show Title Slide.* |
| 2 | **Episode Goal** | Define a common interface so our federated engine can query any provider interchangeably. | *Highlight goal.* |
| 3 | **The Protocol** | `SearchProvider` requires `name: str` and `search(query: Query) -> Iterator[Document]`. | *Show Protocol diagram.* |
| 4 | **Base Architecture** | `BaseProvider` initializes an `AcademicHttpClient` with specific rate limits and polite headers. | *Explain inheritance.* |
| 5 | **Implementation** | Walkthrough of `src/scholar_search/providers/base.py`. | *Transition to code.* |
| 6 | **Verification** | Inspect provider interface compliance. | *Transition to code.* |

## Terminal & Code Walkthrough

1. **Show `base.py`**:
   - Open `src/scholar_search/providers/base.py`.
   - Walk through the `SearchProvider` Protocol and `BaseProvider` class.
