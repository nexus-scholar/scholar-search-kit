"""Normalized models for the tutorial SLR workflow."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ExternalIds:
    doi: str | None = None
    arxiv_id: str | None = None
    pubmed_id: str | None = None

    def __post_init__(self) -> None:
        if self.doi:
            value = self.doi.strip().lower()
            for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
                if value.startswith(prefix):
                    value = value[len(prefix):]
            self.doi = value


@dataclass
class Author:
    family_name: str
    given_name: str | None = None
    orcid: str | None = None

    @property
    def full_name(self) -> str:
        return f"{self.given_name} {self.family_name}" if self.given_name else self.family_name


@dataclass
class Document:
    title: str
    year: int | None = None
    provider: str = "unknown"
    provider_id: str = ""
    external_ids: ExternalIds = field(default_factory=ExternalIds)
    abstract: str | None = None
    authors: list[Author] = field(default_factory=list)
    venue: str | None = None
    url: str | None = None
    query_id: str | None = None
    retrieved_at: datetime | None = None
    cluster_id: int | None = None
    raw_data: dict[str, Any] | None = None

    def mark_retrieved(self) -> None:
        self.retrieved_at = datetime.now(timezone.utc)


@dataclass
class Query:
    text: str
    id: str = "Q001"
    year_min: int | None = None
    year_max: int | None = None
    language: str = "en"
    max_results: int | None = None


@dataclass
class DocumentCluster:
    cluster_id: int
    representative: Document
    members: list[Document]

    @property
    def size(self) -> int:
        return len(self.members)

    @property
    def confidence(self) -> float:
        has_identifier = any(
            member.external_ids.doi or member.external_ids.arxiv_id for member in self.members
        )
        return 1.0 if has_identifier else 0.95