"""HTTP client with caching, rate limiting, and retries for academic APIs."""

import asyncio
import logging
import time
from datetime import timedelta
from typing import Any

import hishel
import httpx

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

    async def wait(self) -> None:
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
            await asyncio.sleep(max(0.01, sleep_time))


class AcademicHttpClient:
    """
    A robust HTTP client wrapped around hishel (httpx caching).
    Handles polite user agents, rate limiting, retries (429/503), timeouts, and caching.
    """

    DEFAULT_TIMEOUT: float = 30.0

    def __init__(self, name: str, rate_limit: float, cache_enabled: bool = True):
        self.name = name
        self.rate_limiter = RateLimiter(rate_limit)
        self.cache_enabled = cache_enabled

        # Ensure cache directory exists
        settings.cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path = settings.cache_dir / "scholar_cache"

        transport = httpx.AsyncHTTPTransport(retries=4)

        if cache_enabled:
            self.client = hishel.AsyncCacheClient(
                transport=transport,
                headers={"User-Agent": f"scholar-search-kit/0.1.0 (mailto:{settings.mailto})"},
            )
        else:
            self.client = httpx.AsyncClient(
                transport=transport,
                headers={"User-Agent": f"scholar-search-kit/0.1.0 (mailto:{settings.mailto})"},
            )

    async def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        timeout: float | None = None,
        headers: dict[str, str] | None = None,
        **kwargs,
    ) -> httpx.Response:
        """Execute a GET request with rate limiting, timeouts, error wrapping, and caching."""
        await self.rate_limiter.wait()

        req_timeout = timeout if timeout is not None else self.DEFAULT_TIMEOUT

        logger.debug(f"[{self.name}] GET {url}")
        try:
            response = await self.client.get(
                url, params=params, timeout=req_timeout, headers=headers, **kwargs
            )
        except httpx.TimeoutException as e:
            raise ProviderError(
                self.name, f"Request timed out after {req_timeout}s: {e}"
            ) from e
        except httpx.RequestError as e:
            raise ProviderError(self.name, f"Network communication error: {e}") from e

        # Check for cache hit in hishel
        if getattr(response.extensions, "from_cache", False):
            logger.debug(f"[{self.name}] Cache hit for {url}")

        if response.status_code == 429:
            raise RateLimitExceededError(
                self.name, "Rate limit exceeded on academic API"
            )
        elif response.status_code >= 400:
            raise ProviderError(
                self.name,
                f"HTTP request failed: {response.text[:200]}",
                status_code=response.status_code,
            )

        return response

    async def close(self) -> None:
        """Close the underlying session."""
        await self.client.aclose()

