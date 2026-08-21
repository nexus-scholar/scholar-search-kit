"""HTTP client with caching, rate limiting, and retries for academic APIs."""

import logging
import time
from datetime import timedelta
from typing import Any, Dict, Optional
import requests
import requests_cache
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import settings
from .exceptions import ProviderError, RateLimitExceededError

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple token bucket rate limiter."""
    def __init__(self, rate: float):
        self.rate = rate
        self.capacity = max(1.0, rate)
        self.tokens = self.capacity
        self.last_update = time.time()

    def wait(self) -> None:
        """Wait until a token is available."""
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
            
            # Sleep a bit before checking again
            sleep_time = (1.0 - self.tokens) / self.rate
            time.sleep(max(0.01, sleep_time))


class AcademicHttpClient:
    """
    A robust HTTP client wrapped around requests-cache.
    Handles polite user agents, rate limiting, retries (429/503), timeouts, and caching.
    """
    DEFAULT_TIMEOUT: float = 30.0

    def __init__(self, name: str, rate_limit: float, cache_enabled: bool = True):
        self.name = name
        self.rate_limiter = RateLimiter(rate_limit)
        self.cache_enabled = cache_enabled
        
        # Ensure cache directory exists
        settings.cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path = settings.cache_dir / "scholar_cache.sqlite"
        
        # Setup session with SQLite caching
        if cache_enabled:
            self.session = requests_cache.CachedSession(
                str(cache_path),
                backend='sqlite',
                expire_after=timedelta(days=settings.cache_expire_days),
                allowable_codes=[200],  # Only cache successful responses
                allowable_methods=['GET']
            )
        else:
            self.session = requests.Session()
        
        # Setup retry strategy (for 429 Too Many Requests and 5xx errors)
        retry_strategy = Retry(
            total=4,
            backoff_factor=2.0,  # 2, 4, 8 seconds
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Setup default headers (Polite Crawling)
        self.session.headers.update({
            "User-Agent": f"scholar-search-kit/0.1.0 (mailto:{settings.mailto})"
        })

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        """Execute a GET request with rate limiting, timeouts, error wrapping, and caching."""
        self.rate_limiter.wait()
        
        req_timeout = timeout if timeout is not None else self.DEFAULT_TIMEOUT
        
        logger.debug(f"[{self.name}] GET {url}")
        try:
            response = self.session.get(
                url,
                params=params,
                timeout=req_timeout,
                headers=headers,
                **kwargs
            )
        except requests.Timeout as e:
            raise ProviderError(self.name, f"Request timed out after {req_timeout}s: {e}") from e
        except requests.RequestException as e:
            raise ProviderError(self.name, f"Network communication error: {e}") from e
        
        if getattr(response, "from_cache", False):
            logger.debug(f"[{self.name}] Cache hit for {url}")
        
        if response.status_code == 429:
            raise RateLimitExceededError(self.name, "Rate limit exceeded on academic API")
        elif response.status_code >= 400:
            raise ProviderError(self.name, f"HTTP request failed: {response.text[:200]}", status_code=response.status_code)
            
        return response

    def close(self) -> None:
        """Close the underlying session."""
        self.session.close()
