# Episode 7: Exception Hierarchy for Resilient Search

**Objective:** Build a typed exception hierarchy to distinguish recoverable network faults from permanent failures.

## Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | External APIs fail constantly. Our system must fail gracefully and predictably. | *Show Title Slide.* |
| 2 | **Episode Goal** | Unhandled exceptions crash large workflows. A typed hierarchy allows targeted retry strategies. | *Highlight goal.* |
| 3 | **The Exception Tree** | `ScholarSearchError` branches into `ProviderError`, `RateLimitExceededError`, `InvalidQueryError`, and `VerificationError`. | *Show hierarchy diagram.* |
| 4 | **Provider Context** | Every provider error prefixes the source (e.g. `[openalex] ...`) and carries the HTTP status code. | *Explain provider tagging.* |
| 5 | **Implementation** | We define our exceptions in `src/scholar_search/exceptions.py`. | *Transition to code.* |
| 6 | **Verification** | We run our exception tests. | *Transition to Terminal.* |

## Terminal & Code Walkthrough

1. **Show `exceptions.py`**:
   - Open `src/scholar_search/exceptions.py`.
   - Walk through the class definitions.
2. **Show Usage**:
   - Explain how `AcademicHttpClient` wraps raw `requests` errors into `ProviderError` and `RateLimitExceededError`.
