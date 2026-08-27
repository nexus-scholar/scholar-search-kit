# Lesson 3.1: Exception Hierarchy for Resilient Search (`exceptions.py`)

## 1. Scientific Motivation & Context
Scholarly literature search involves querying multiple external public APIs across the internet. External failures are diverse: HTTP 429 rate limit spikes, HTTP 401/403 credential errors, 502/504 gateway timeouts, malformed responses, or XML parsing errors. Without a typed exception hierarchy, calling code cannot distinguish transient errors (which should be retried) from permanent authentication or query errors (which must halt immediately).

---

## 2. Component Contract & Implementation

* **Module**: `scholar_search.exceptions`
* **Hierarchy**:

```python
"""Custom exceptions for scholar-search-kit."""


class ScholarSearchError(Exception):
    """Base exception for all scholar-search errors."""

    pass


class ProviderError(ScholarSearchError):
    """Raised when an external academic provider returns an error."""

    def __init__(self, provider: str, message: str, status_code: int | None = None):
        self.provider = provider
        self.status_code = status_code
        super().__init__(
            f"[{provider}] {message}"
            + (f" (HTTP {status_code})" if status_code else "")
        )


class RateLimitExceededError(ProviderError):
    """Raised when an API rate limit is exceeded (HTTP 429)."""

    def __init__(self, provider: str, message: str = "Rate limit exceeded"):
        super().__init__(provider=provider, message=message, status_code=429)


class InvalidQueryError(ScholarSearchError):
    """Raised when a search query cannot be parsed or translated."""

    pass


class VerificationError(ScholarSearchError):
    """Raised when document verification or hydration fails."""

    pass
```

---

## 3. Invariants & Rules

1. **Provider Context**: All `ProviderError` exceptions include `provider: str` and format as `f"[{provider}] {message}"`.
2. **HTTP Status Encapsulation**: When an HTTP status code is present, it is recorded in `error.status_code`.
3. **Structured Specialization**:
   - `RateLimitExceededError` specifically models HTTP 429 rate limiting.
   - `InvalidQueryError` captures query lexing/syntax failures.
   - `VerificationError` captures failure during Crossref/OpenAlex verification or hydration.

---

## 4. Verification & Automated Tests

```python
from scholar_search.exceptions import (
    ScholarSearchError,
    ProviderError,
    RateLimitExceededError,
)


def test_exception_formatting():
    err = RateLimitExceededError(provider="crossref", message="Too many requests")
    assert err.provider == "crossref"
    assert err.status_code == 429
    assert "[crossref]" in str(err)
    assert issubclass(RateLimitExceededError, ProviderError)
    assert issubclass(ProviderError, ScholarSearchError)
```
