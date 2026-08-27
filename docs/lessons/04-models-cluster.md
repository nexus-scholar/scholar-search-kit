# Lesson 2.4: Clusters & Non-Destructive Merging (`DocumentCluster`)

## 1. Scientific Motivation & Context
Deduplication directly alters the statistical denominator of any literature review. When duplicate records are dropped naively without grouping, the research becomes unauditable: reviewers cannot verify why two records were merged or what provider-specific metadata was discarded. Grouping duplicates into `DocumentCluster` preserves the full provenance trail while allowing intelligent metadata merging into the representative record.

---

## 2. Component Contract & Implementation

* **Module**: `scholar_search.models`
* **Dataclass**: `DocumentCluster`

```python
from dataclasses import dataclass
from .models import Document


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
            member.external_ids.doi
            or member.external_ids.arxiv_id
            or member.external_ids.pubmed_id
            for member in self.members
        )
        return 1.0 if has_identifier else 0.95
```

---

## 3. Invariants & Usage Rules

1. **Non-Destructive Preservation**: All duplicate records remain accessible in `cluster.members`.
2. **Canonical Representative**: `cluster.representative` holds the merged metadata record intended for exports.
3. **Confidence Evidence Metric**:
   - `1.0`: Exact persistent identifier match (DOI, arXiv ID, PMID, etc.).
   - `0.95`: Fuzzy title similarity ($\ge 97\%$).

---

## 4. Verification & Automated Tests

Run with `pytest tests/test_models.py -k "test_document_cluster"`:

```python
from scholar_search.models import Document, DocumentCluster, ExternalIds


def test_document_cluster():
    d1 = Document(
        "Paper A", external_ids=ExternalIds(doi="10.1/abc"), provider="openalex"
    )
    d2 = Document(
        "Paper A", external_ids=ExternalIds(doi="10.1/abc"), provider="crossref"
    )

    cluster = DocumentCluster(cluster_id=1, representative=d1, members=[d1, d2])

    assert cluster.size == 2
    assert cluster.confidence == 1.0
    assert d1 in cluster.members
    assert d2 in cluster.members
```
