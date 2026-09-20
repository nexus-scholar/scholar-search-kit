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

    def __init__(
        self,
        name: str,
        rate_limit: float,
        cache_enabled: bool = True,
        max_retries: int = 3,
        base_delay: float = 1.0,
    ):
        self.name = name
        self.rate_limiter = RateLimiter(rate_limit)
        self.cache_enabled = cache_enabled
        self.max_retries = max_retries
        self.base_delay = base_delay

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

    async def post(
        self,
        url: str,
        json: dict | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        """Execute a POST request with rate limiting, retries, and exponential backoff.

        Args:
            url: Target URL.
            json: JSON-serializable request body.
            params: Query parameters.
            headers: Extra headers merged with ``{"Accept": "application/json"}``.
            timeout: Per-request timeout in seconds (default: 30).

        Returns:
            Raw ``httpx.Response``; caller decides parsing.

        Raises:
            ProviderError: After all retries exhausted on network/HTTP errors.
            RateLimitExceededError: After all retries exhausted on HTTP 429.
        """
        req_timeout = timeout if timeout is not None else self.DEFAULT_TIMEOUT
        merged_headers = {"Accept": "application/json"}
        if headers:
            merged_headers.update(headers)

        last_exc: Exception | None = None

        for attempt in range(self.max_retries + 1):
            await self.rate_limiter.wait()

            logger.debug(f"[{self.name}] POST {url} (attempt {attempt + 1})")
            try:
                response = await self.client.post(
                    url,
                    json=json,
                    params=params,
                    timeout=req_timeout,
                    headers=merged_headers,
                )
            except httpx.TimeoutException as exc:
                last_exc = exc
                logger.warning(
                    f"[{self.name}] Timeout on attempt {attempt + 1}: {exc}"
                )
                if attempt < self.max_retries:
                    await asyncio.sleep(self.base_delay * (2 ** attempt))
                    continue
                raise ProviderError(
                    self.name, f"Request timed out after {req_timeout}s: {exc}"
                ) from exc
            except httpx.RequestError as exc:
                last_exc = exc
                logger.warning(
                    f"[{self.name}] Network error on attempt {attempt + 1}: {exc}"
                )
                if attempt < self.max_retries:
                    await asyncio.sleep(self.base_delay * (2 ** attempt))
                    continue
                raise ProviderError(
                    self.name, f"Network communication error: {exc}"
                ) from exc

            # Handle HTTP error status codes
            if response.status_code == 429:
                retry_after = response.headers.get("retry-after")
                delay = float(retry_after) if retry_after else self.base_delay * (2 ** attempt)
                logger.warning(
                    f"[{self.name}] 429 on attempt {attempt + 1}, retry after {delay}s"
                )
                if attempt < self.max_retries:
                    await asyncio.sleep(delay)
                    continue
                raise RateLimitExceededError(
                    self.name, "Rate limit exceeded on academic API"
                )
            elif response.status_code >= 400:
                if attempt < self.max_retries:
                    await asyncio.sleep(self.base_delay * (2 ** attempt))
                    continue
                raise ProviderError(
                    self.name,
                    f"HTTP request failed: {response.text[:200]}",
                    status_code=response.status_code,
                )

            return response

        # Unreachable but satisfies type checker
        raise ProviderError(self.name, "POST failed after all retries")

    async def close(self) -> None:
        """Close the underlying session."""
        await self.client.aclose()

