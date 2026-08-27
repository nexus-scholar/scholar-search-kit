# Lesson 6.2: Document Verification & Hallucination Detection (`verifier.py`)

## 1. Scientific Motivation & Context
Large Language Models (LLMs) and automated agent pipelines frequently generate synthetic literature citations containing invented DOIs, phantom authors, or slight title distortions. Furthermore, user-provided citation lists (e.g. legacy RIS files or unverified bibliographies) often lack abstracts, venues, or publication dates.

Our `DocumentVerifier` solves this by cross-referencing records against Crossref's 150M+ registered works and hydrating missing metadata from OpenAlex.

---

## 2. Component Contract & Implementation

* **Module**: `scholar_search.verifier`
* **Class**: `DocumentVerifier`
* **Dataclass**: `VerificationResult`

```python
from dataclasses import dataclass, field
from scholar_search.models import Document


@dataclass
class VerificationResult:
    document: Document
    is_verified: bool
    confidence: float = 0.0
    matched_doi: str | None = None
    matched_title: str | None = None
    issues: list[str] = field(default_factory=list)
```

### Verification & Hydration Capabilities
1. **DOI Verification (`verify_by_doi`)**: Queries Crossref directly. Validates if the DOI exists and compares the official title against the claimed title.
2. **Title Bibliographic Verification (`verify_by_title`)**: Queries Crossref's `query.bibliographic` engine for un-identified citations. Flags hallucinations if similarity $< 0.85$.
3. **Metadata Hydration (`hydrate_metadata`)**: If a document has a verified DOI or title, queries OpenAlex to backfill missing abstract prose, venue names, publication year, and citations count.

---

## 3. Verification & Automated Tests

Run with `pytest tests/test_verifier.py`:

```python
from scholar_search.verifier import DocumentVerifier
from scholar_search.models import Document, ExternalIds


def test_verify_document_by_doi():
    verifier = DocumentVerifier()
    doc = Document(
        title="Attention Is All You Need",
        external_ids=ExternalIds(doi="10.48550/arXiv.1706.03762"),
    )
    result = verifier.verify_document(doc)
    assert result.is_verified is True
    assert result.confidence >= 0.80


def test_detect_hallucinated_document():
    verifier = DocumentVerifier()
    fake_doc = Document(
        title="Quantum Teleportation of Bananas using Convolutional Neural Networks",
        external_ids=ExternalIds(doi="10.1000/182_fake_banana_hallucination"),
    )
    result = verifier.verify_document(fake_doc)
    assert result.is_verified is False
    assert len(result.issues) > 0
```
