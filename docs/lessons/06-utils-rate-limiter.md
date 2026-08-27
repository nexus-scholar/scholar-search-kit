# Lesson 3.2: Rate Limiting with Token Buckets (`http_client.py`)

## 1. Scientific Motivation & Context
Academic APIs enforce strict rate limits to protect public infrastructure (e.g. arXiv 1 req/s, OpenAlex 10 req/s polite pool, Crossref 5 req/s polite pool, Semantic Scholar 1 req/s). A client-side rate limiter regulates request bursts and prevents uncoordinated concurrency from triggering temporary IP bans.

---

## 2. Component Contract & Implementation

* **Module**: `scholar_search.http_client`
* **Class**: `RateLimiter`

```python
import time


class RateLimiter:
    """Token bucket rate limiter ensuring polite client-side request rates."""

    def __init__(self, rate: float):
        self.rate = rate
        self.capacity = max(1.0, rate)
        self.tokens = self.capacity
        self.last_update = time.time()

    def wait(self) -> None:
        """Wait until at least 1.0 token is available."""
        if self.rate <= 0:
            return

        while True:
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_update = now

            if self.tokens >= 1.0:
                self.tokens -= 1.0
                return

            sleep_time = (1.0 - self.tokens) / self.rate
            time.sleep(max(0.01, sleep_time))
```

---

## 3. Mathematical Refill Model

$$\text{tokens}(t) = \min\Big(\text{capacity},\ \text{tokens}(t_{last}) + (t - t_{last}) \times \text{rate}\Big)$$

1. **Burst Capacity**: Allows up to `capacity` requests instantaneously if the system has been idle.
2. **Smooth Replenishment**: Continuously refills at `rate` tokens per second.
3. **Adaptive Sleep**: Computes the exact duration needed before the next token is ready.
