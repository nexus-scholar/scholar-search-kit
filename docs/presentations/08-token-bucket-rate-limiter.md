# Episode 8: Rate Limiting with Token Buckets

**Objective:** Build a thread-safe, mathematically sound rate limiter to ensure polite interactions with upstream providers.

## 🎬 Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | We are going to hit academic APIs. If we do it too fast, we get banned. | *Show Title Slide.* |
| 2 | **Episode Goal** | `time.sleep(1)` is terrible. It wastes time when the API allows bursts. We need a token bucket. | *Highlight the goal block.* |
| 3 | **The Token Bucket Algorithm** | Imagine a bucket filling with coins at a steady rate. Making a request costs a coin. | *Point to the diagram.* |
| 4 | **Implementation: `TokenBucket`** | The beauty of this is we don't need background threads. We just use math against the system clock. | *Explain the math.* |
| 5 | **Why not a Sliding Window?** | Token buckets use $O(1)$ memory. We don't have to maintain an array of 1,000 timestamps just to check limits. | *Explain efficiency.* |
| 6 | **Verification** | Let's write the code and test the timing logic. | *Transition to Terminal.* |

## 💻 Terminal & Code Walkthrough

1. **Show `rate_limit.py`**:
   - Open `src/scholar_search/utils/rate_limit.py`.
   - Walk through the `TokenBucket` class and the `consume` method.
2. **Explain `time.monotonic()`**:
   - Emphasize why we use `time.monotonic()` instead of `time.time()` (protection against clock drift).
3. **Run the Tests**:
   - In the terminal, run: `pytest -k "test_rate_limit"`
   - Show how the test verifies refill behavior.
