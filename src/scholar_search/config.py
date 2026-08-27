"""Configuration management for scholar-search-kit."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Main configuration settings loaded from environment or .env file."""

    # Polite crawling email (required for Crossref and OpenAlex best performance)
    mailto: str = Field(
        default="student@university.edu", description="Email for polite API crawling"
    )

    # API Keys
    openalex_key: str | None = Field(
        default=None, description="OpenAlex Premium API Key (Optional)"
    )
    s2_key: str | None = Field(
        default=None, description="Semantic Scholar API Key (Optional but recommended)"
    )

    # Cache settings
    cache_dir: Path = Field(
        default=Path(".cache"), description="Directory to store SQLite cache"
    )
    cache_expire_days: int = Field(
        default=30, description="Number of days to keep API responses cached"
    )

    # Rate limits (Requests per second)
    rate_limit_openalex: float = Field(
        default=10.0, description="OpenAlex requests per second"
    )
    rate_limit_crossref: float = Field(
        default=5.0, description="Crossref requests per second (with mailto)"
    )
    rate_limit_s2: float = Field(
        default=1.0, description="Semantic Scholar requests per second (no key)"
    )
    rate_limit_pubmed: float = Field(
        default=3.0, description="PubMed requests per second (no key)"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="SCHOLAR_",
        extra="ignore",
    )


# Global settings instance
settings = Settings()
