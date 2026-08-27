"""Custom exceptions for scholar-search-kit."""


class ScholarSearchError(Exception):
    """Base exception for all scholar-search errors."""


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
    """Raised when an API rate limit is exceeded."""

    def __init__(self, provider: str, message: str = "Rate limit exceeded"):
        super().__init__(provider=provider, message=message, status_code=429)


class InvalidQueryError(ScholarSearchError):
    """Raised when a search query cannot be parsed or translated."""


class VerificationError(ScholarSearchError):
    """Raised when document verification or hydration fails."""
