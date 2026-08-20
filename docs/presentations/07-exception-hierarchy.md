# Episode 7: Exception Hierarchy for Resilient Search

**Objective:** Implement a robust error taxonomy to prevent long-running searches from crashing fatally on transient API issues.

## 🎬 Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | We have our models. Now we need to prepare for failure. | *Show Title Slide.* |
| 2 | **Episode Goal** | Ingesting large volumes of data means we *will* hit network disconnects and rate limits. We need a way to catch and handle them safely. | *Highlight the goal block.* |
| 3 | **The Hierarchy** | We build a tree of exceptions inheriting from a base `SearchException`. | *Point to the diagram.* |
| 4 | **Why Custom Exceptions?** | We want to decouple our domain logic from `requests`. If we switch to `httpx`, our error handling doesn't break. | *Explain abstraction.* |
| 5 | **Implementation: `RateLimitError`** | We don't just throw errors; we throw data. A rate limit error will carry the exact number of seconds we need to sleep. | *Explain `retry_after`.* |
| 6 | **Verification** | Let's define these and write a test to catch them. | *Transition to Terminal.* |

## 💻 Terminal & Code Walkthrough

1. **Show `exceptions.py`**:
   - Open `src/scholar_search/utils/exceptions.py`.
   - Walk through the class definitions.
2. **Show payload passing**:
   - Show how `RateLimitError(retry_after=60)` works.
3. **Run the Tests**:
   - In the terminal, run: `pytest -k "test_exceptions"`
   - Prove that catching `SearchException` safely catches all subclasses.
