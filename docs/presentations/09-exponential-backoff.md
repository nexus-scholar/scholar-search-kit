# Episode 9: Exponential Backoff & Rate Limit Retries

**Objective:** Use Python decorators to cleanly inject retry logic around flaky network calls without polluting the business logic.

## 🎬 Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | We have our Exception hierarchy. Now we use it to make our code bulletproof. | *Show Title Slide.* |
| 2 | **Episode Goal** | We want to write code assuming the network is perfect, and let a wrapper handle the failures. | *Highlight the goal block.* |
| 3 | **The Decorator Pattern** | By wrapping our functions, the retry logic acts as a shield between us and the API. | *Point to the diagram.* |
| 4 | **Implementation: `retry_with_backoff`** | If the network drops, we try again, but we back off exponentially to avoid hammering a struggling server. | *Explain backoff and jitter.* |
| 5 | **Implementation: `retry_on_rate_limit`** | If we hit a 429, the server tells us exactly how long to wait. We read that value from our exception. | *Explain extracting `retry_after`.* |
| 6 | **Verification** | Let's mock a flaky function and watch the decorator save the day. | *Transition to Terminal.* |

## 💻 Terminal & Code Walkthrough

1. **Show `retry.py`**:
   - Open `src/scholar_search/utils/retry.py`.
   - Walk through the `retry_with_backoff` and `retry_on_rate_limit` decorators.
2. **Explain the magic**:
   - Show how `functools.wraps` preserves the original function signatures.
3. **Run the Tests**:
   - In the terminal, run: `pytest -k "test_retry"`
   - Show the logs indicating the sleep periods between retries.
