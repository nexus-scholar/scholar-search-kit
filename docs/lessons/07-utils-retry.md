# Lesson 3.3: Exponential Backoff, SQLite Caching, & Timeouts (`AcademicHttpClient`)

## 1. Scientific Motivation & Context
Network connections drop, academic proxy gateways experience momentary 502/503/504 hiccups, and academic servers experience load spikes. Instead of crashing multi-hour systematic literature searches, requests must automatically retry with exponential backoff, obey socket timeouts, and persist cached responses in SQLite to prevent redundant API calls.

---

## 2. Component Contract & Implementation

* **Module**: `scholar_search.http_client`
* **Class**: `AcademicHttpClient`

```python
import logging
from datetime import timedelta
from typing import Any, Dict, Optional
import requests
import requests_cache
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import settings
from .exceptions import ProviderError, RateLimitExceededError


class AcademicHttpClient:
    DEFAULT_TIMEOUT: float = 30.0

    def __init__(self, name: str, rate_limit: float, cache_enabled: bool = True):
        self.name = name
        self.rate_limiter = RateLimiter(rate_limit)

        # 1. SQLite Caching Session
        settings.cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path = settings.cache_dir / "scholar_cache.sqlite"
        if cache_enabled:
            self.session = requests_cache.CachedSession(
                str(cache_path),
                backend="sqlite",
                expire_after=timedelta(days=settings.cache_expire_days),
                allowable_codes=[200],
                allowable_methods=["GET"],
            )
        else:
            self.session = requests.Session()

        # 2. Retry Strategy (Exponential Backoff on 429 and 5xx)
        retry_strategy = Retry(
            total=4,
            backoff_factor=2.0,  # 2s, 4s, 8s backoff
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # 3. Polite Headers
        self.session.headers.update(
            {"User-Agent": f"scholar-search-kit/0.1.0 (mailto:{settings.mailto})"}
        )

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> requests.Response:
        self.rate_limiter.wait()
        req_timeout = timeout if timeout is not None else self.DEFAULT_TIMEOUT

        try:
            response = self.session.get(
                url, params=params, timeout=req_timeout, **kwargs
            )
        except requests.Timeout as e:
            raise ProviderError(
                self.name, f"Request timed out after {req_timeout}s: {e}"
            ) from e
        except requests.RequestException as e:
            raise ProviderError(self.name, f"Network communication error: {e}") from e

        if response.status_code == 429:
            raise RateLimitExceededError(self.name)
        elif response.status_code >= 400:
            raise ProviderError(
                self.name,
                f"HTTP request failed: {response.text[:200]}",
                status_code=response.status_code,
            )

        return response
```

---

## 3. Invariants & Resilience Features

1. **Deterministic Caching**: Identical queries return instant local cache hits (`response.from_cache == True`) with configurable expiration (default 30 days).
2. **Explicit 30s Timeouts**: Prevents indefinite socket hangs when external academic gateways stall.
3. **Exponential Retry Backoff**: Automatic retry for transient 429 and 5xx gateway errors.
4. **Polite Crawling**: Injects `mailto` user agent headers to qualify for OpenAlex and Crossref polite API pools.
