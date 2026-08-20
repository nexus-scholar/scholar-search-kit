# Lesson 3.2: Rate Limiting with Token Buckets (`rate_limit.py`)

**Status**: 🟡 **Lesson Milestone Target** / 🔵 **Reference: `strategy-pipeline/src/slr/utils/rate_limit.py`**

---

## 1. Scientific Motivation & Context
Academic APIs enforce rate limits to protect public infrastructure (e.g. arXiv 3 req/s, OpenAlex 10 req/s polite pool, Crossref 50 req/s polite pool). A client-side rate limiter reduces client-generated request bursts and prevents uncoordinated concurrency from triggering temporary IP bans. However, because remote servers may enforce dynamic load shedding or shared-IP restrictions, client rate limiting must always be paired with HTTP 429 backoff handling.

## 2. Reference Architecture Analysis
* **Reference Source**: `strategy-pipeline/src/slr/utils/rate_limit.py`
* **Implementations**:
  * `TokenBucket`: Continuous token replenishment with burst capacity and thread-safe locking.
  * `SlidingWindowRateLimiter`: Deque-based timestamp sliding window.
  * `RateLimitDecorator`: Function wrapper enforcing rate limits.

## 3. Explicit Component Contract

### Class Definition: `TokenBucket`
* **Mathematical Refill Model**:
  $$\text{tokens}(t) = \min\Big(\text{capacity},\ \text{tokens}(t_{last}) + (t - t_{last}) \times \text{rate}\Big)$$
* **Methods**:
  * `__init__(rate: float, capacity: int)`:
    * `rate`: Tokens added per second ($> 0$).
    * `capacity`: Maximum token accumulation (default: $5 \times \text{rate}$).
  * `consume(tokens: int = 1) -> bool`:
    * Non-blocking. Consumes tokens if available and returns `True`, else `False`.
  * `wait_for_token(tokens: int = 1, timeout: Optional[float] = None) -> bool`:
    * Blocking. Computes deficit $\Delta = \text{tokens} - \text{current\_tokens}$.
    * Calculates sleep interval: $t_{sleep} = \min(\Delta / \text{rate}, 1.0)$.
    * Blocks until tokens available or `timeout` exceeded. Returns `True` if acquired, `False` on timeout.

### Invariants & Thread Safety
1. **Thread Lock**: All state access (`tokens`, `last_update`) must be guarded by `threading.Lock()`.
2. **Clock Source**: Must use `time.monotonic()` to guard against system clock adjustments.

## 4. Verification & Falsifying Tests

```python
import time
from scholar_search.utils.rate_limit import TokenBucket

def test_token_bucket_burst_and_refill():
    bucket = TokenBucket(rate=10.0, capacity=5)
    
    # Can burst up to capacity
    assert bucket.consume(5) is True
    # Immediate next consumption fails
    assert bucket.consume(1) is False
    
    # After 0.25s, at least 2 tokens refill (0.25 * 10 = 2.5)
    time.sleep(0.25)
    assert bucket.consume(2) is True

def test_token_bucket_wait_timeout():
    bucket = TokenBucket(rate=1.0, capacity=1)
    bucket.consume(1)
    # Waiting with short timeout should fail
    assert bucket.wait_for_token(tokens=10, timeout=0.1) is False
```

## 5. AI Build Prompt

```text
Implement TokenBucket, SlidingWindowRateLimiter, and RateLimitDecorator in scholar_search/utils/rate_limit.py following Lesson 3.2.
Ensure thread-safety with threading.Lock, monotonic clock timing, burst capacity, and blocking wait_for_token logic.
Add unit tests in tests/test_rate_limit.py.
```
