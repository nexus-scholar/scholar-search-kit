"""Normalized models for the SLR and scholarly search workflow."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class ExternalIds:
    doi: str | None = None
    arxiv_id: str | None = None
    pubmed_id: str | None = None
    openalex_id: str | None = None
    s2_id: str | None = None

    def __post_init__(self) -> None:
        if self.doi:
            value = self.doi.strip().lower()
            for prefix in (
                "https://doi.org/",
                "http://doi.org/",
                "https://dx.doi.org/",
                "http://dx.doi.org/",
                "doi:",
            ):
                value = value.removeprefix(prefix)
            value = value.strip()
            self.doi = value if value else None
        else:
            self.doi = None

        if self.arxiv_id:
            val = self.arxiv_id.strip()
            for prefix in ("arxiv:", "arXiv:"):
                val = val.removeprefix(prefix)
            val = val.strip()
            self.arxiv_id = val if val else None


@dataclass
class Author:
    family_name: str
    given_name: str | None = None
    orcid: str | None = None

    @property
    def full_name(self) -> str:
        return (
            f"{self.given_name} {self.family_name}"
            if self.given_name
            else self.family_name
        )


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

    # Workspace & Provenance Identification
    workspace_id: str | None = None
    sources: list[dict[str, Any]] = field(default_factory=list)
    oa_locations: list[dict[str, Any]] = field(default_factory=list)

    # Snowballing & Enhanced Metadata
    citations_count: int | None = None
    references_count: int | None = None
    citation_intents: list[str] = field(
        default_factory=list
    )  # e.g. "methodology" from S2
    mesh_terms: list[str] = field(
        default_factory=list
    )  # Medical Subject Headings from PubMed
    tldr: str | None = None  # AI Summary from Semantic Scholar

    query_id: str | None = None
    retrieved_at: datetime | None = None
    cluster_id: int | None = None
    raw_data: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        import html
        import re

        if self.title:
            t = html.unescape(self.title)
            t = re.sub(r"<[^>]+>", "", t)
            self.title = re.sub(r"\s+", " ", t).strip()
        else:
            self.title = "Untitled"

        if self.venue:
            v = html.unescape(self.venue)
            v = re.sub(r"<[^>]+>", "", v)
            self.venue = re.sub(r"\s+", " ", v).strip()

        if self.abstract:
            a = html.unescape(self.abstract)
            # Strip JATS XML and general XML/HTML tags
            a = re.sub(r"<jats:[^>]+>", "", a)
            a = re.sub(r"</jats:[^>]+>", "", a)
            a = re.sub(r"<[^>]+>", "", a)
            self.abstract = re.sub(r"\s+", " ", a).strip()

        if not self.sources and self.provider and self.provider != "unknown":
            self.sources.append(
                {
                    "provider": self.provider,
                    "id": self.provider_id,
                }
            )

    def mark_retrieved(self) -> None:
        self.retrieved_at = datetime.now(UTC)


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
            member.external_ids.doi or member.external_ids.arxiv_id
            for member in self.members
        )
        return 1.0 if has_identifier else 0.95
