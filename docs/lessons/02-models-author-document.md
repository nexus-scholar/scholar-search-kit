# Lesson 2.2: The Normalized Document & Author Model

## 1. Scientific Motivation & Context
Academic documents from different sources arrive in incompatible schemas (OpenAlex JSON, Crossref works JSON, PubMed XML, arXiv Atom XML, Semantic Scholar bulk JSON). To enable cross-provider search, deduplication, verification, and export without vendor lock-in, all records must normalize into a single canonical `Document` model while strictly preserving source provenance and citation metadata.

---

## 2. Component Contracts & Implementation

* **Module**: `scholar_search.models`
* **Dataclasses**: `Author`, `Document`

```python
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .models import ExternalIds


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

    def mark_retrieved(self) -> None:
        self.retrieved_at = datetime.now(timezone.utc)
```

---

## 3. Invariants & Data Integrity Rules

1. **Title Required**: `title` is mandatory for every document.
2. **Nullable Year**: If unknown, `year` remains `None` (never default to `0` or `1970` which corrupts chronological filtering).
3. **Automatic ExternalIds**: Instantiating a `Document` always prepares an `ExternalIds` container.
4. **UTC Audit Timestamps**: `mark_retrieved()` records standard UTC timestamps (`datetime.now(timezone.utc)`) ensuring auditable research logs across timezones.
5. **Enriched Context**: Preserves biomedical `mesh_terms`, Semantic Scholar `citation_intents`, and `tldr` AI summaries when available.

---

## 4. Verification & Automated Tests

Run with `pytest tests/test_models.py -k "test_author or test_document"`:

```python
from datetime import timezone
from scholar_search.models import Author, Document


def test_author_properties():
    a1 = Author(family_name="Turing", given_name="Alan")
    assert a1.full_name == "Alan Turing"

    a2 = Author(family_name="Euclid")
    assert a2.full_name == "Euclid"


def test_document_defaults_and_retrieval():
    doc = Document(title="Computing Machinery and Intelligence", year=1950)
    assert doc.external_ids is not None
    assert doc.authors == []
    assert doc.retrieved_at is None

    doc.mark_retrieved()
    assert doc.retrieved_at is not None
    assert doc.retrieved_at.tzinfo == timezone.utc
```
