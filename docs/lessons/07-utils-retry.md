# Lesson 3.3: Exponential Backoff & Rate Limit Retries (`retry.py`)

## 1. Scientific Motivation & Context
Network connections drop, proxy servers experience momentary glitch states, and academic APIs occasionally return HTTP 500/502/503/504 errors or HTTP 429 rate limit errors. Instead of failing an entire multi-hour systematic search, operations must retry with exponential backoff and obey server-instructed `Retry-After` cooldown intervals.

## 2. Reference Architecture Analysis
* **Reference Source**: `strategy-pipeline/src/slr/utils/retry.py`
* **Implementations**:
  * `@retry_with_backoff`: Generic decorator applying exponential backoff to transient network failures.
  * `@retry_on_rate_limit`: Specialized decorator inspecting `RateLimitError.retry_after` headers.
  * `RetryableOperation`: Context manager alternative for structured blocks.

## 3. Explicit Component Contract

### 3.1 `@retry_with_backoff`
* **Signature**:
  ```python
  def retry_with_backoff(
      max_retries: int = 3,
      base_delay: float = 1.0,
      backoff_factor: float = 2.0,
      max_delay: float = 60.0,
      exceptions: Tuple[Type[Exception], ...] = (NetworkError, RateLimitError),
      on_retry: Optional[Callable[[Exception, int], None]] = None,
  ) -> Callable: ...
  ```
* **Delay Formula**:
  $$d_i = \min(\text{base\_delay} \times \text{backoff\_factor}^i,\ \text{max\_delay})$$
* **Behavior**:
  * Catches only specified `exceptions`. Unlisted exceptions re-raise immediately.
  * Sleeps $d_i$ seconds before attempt $i+1$.
  * On final attempt exhaustion, re-raises the last caught exception.

### 3.2 `@retry_on_rate_limit`
* **Signature**:
  ```python
  def retry_on_rate_limit(
      max_retries: int = 5,
      base_delay: float = 5.0,
      backoff_factor: float = 2.0,
  ) -> Callable: ...
  ```
* **Dynamic Header Handling**:
  * If the caught `RateLimitError` has `retry_after` set, logs and sleeps for `retry_after` seconds.

## 4. Verification & Falsifying Tests

```python
import pytest
from scholar_search.utils.exceptions import NetworkError, AuthenticationError
from scholar_search.utils.retry import retry_with_backoff

def test_retry_eventual_success():
    attempts = 0
    
    @retry_with_backoff(max_retries=3, base_delay=0.01)
    def flaky_call():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise NetworkError("test", "Connection dropped")
        return "success"
        
    assert flaky_call() == "success"
    assert attempts == 3

def test_non_retryable_exception_fails_immediately():
    attempts = 0
    
    @retry_with_backoff(max_retries=3, base_delay=0.01)
    def auth_fail():
        nonlocal attempts
        attempts += 1
        raise AuthenticationError("test", "Invalid API key")
        
    with pytest.raises(AuthenticationError):
        auth_fail()
    assert attempts == 1  # Did not retry
```

## 5. AI Build Prompt

```text
Implement retry_with_backoff, retry_on_rate_limit, and RetryableOperation in scholar_search/utils/retry.py following Lesson 3.3.
Support exponential backoff, maximum delay caps, selective exception filtering, on_retry callbacks, and Retry-After header extraction.
Add unit tests in tests/test_retry.py.
```
