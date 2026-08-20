# Lesson 2.4: Clusters & Non-Destructive Merging (`DocumentCluster`)

**Status**: 🟢 **[🟢 Implemented v0.1.0]** (Baseline in `models.py`) / 🟡 **[🟡 Lesson Milestone Target]** (Extended Metadata & Match Method)

---

## 1. Scientific Motivation & Context

Deduplication directly alters the statistical denominator of any literature collection. When deduplication permanently drops records, the research becomes unauditable: peers cannot verify why two records were merged, what provider-specific metadata was discarded, or whether a false merge corrupted the study set. Grouping duplicates into `DocumentCluster` instances preserves the entire evidence trail without data loss.

---

## 2. Reference Architecture Analysis

* **Reference Source**: `strategy-pipeline/src/slr/core/models.py::DocumentCluster`
* **Observed Behavior**:
  * Fields: `cluster_id`, `representative: Document`, `members: List[Document]`.
  * Aggregated metadata: `all_dois: List[str]`, `all_arxiv_ids: List[str]`, `provider_counts: Dict[str, int]`.
  * Evidence metric: Reports `1.0` if an exact persistent identifier match occurred; `0.95` for conservative title similarity.

---

## 3. Explicit Component Contracts

### 🟢 Baseline Implementation Contract (`v0.1.0`)

* **Fields**:
  * `cluster_id`: `int` — Unique sequential cluster identifier.
  * `representative`: `Document` — Canonical representative chosen for export.
  * `members`: `List[Document]` — Complete list of merged member records.
* **Derived Properties**:
  * `size -> int`: `len(self.members)`.
  * `confidence -> float`: `1.0` if any member has an external ID else `0.95`.

### 🟡 Lesson Milestone Target Contract

* **Target Fields**:
  * `all_dois`: `List[str] = field(default_factory=list)`
  * `all_arxiv_ids`: `List[str] = field(default_factory=list)`
  * `provider_counts`: `Dict[str, int] = field(default_factory=dict)`
  * `match_method`: `Optional[str] = None` (`"exact_doi"`, `"exact_arxiv_id"`, `"fuzzy_title"`)

### Scientific Caution on Confidence Scores

> [!NOTE]
> The `0.95` and `1.0` scores are heuristic evidence markers, not calibrated Bayesian probabilities. In scientific publications and formal review protocols, researchers should inspect `match_method` (`exact_doi`, `exact_arxiv_id`, `fuzzy_title`) rather than treating `confidence` as a statistical probability.

---

## 4. Verification & Falsifying Tests

### 🟢 Baseline Verification Test (Current Implementation)

```python
from scholar_search.models import Document, DocumentCluster, ExternalIds

def test_document_cluster_baseline():
    d1 = Document("Paper A", external_ids=ExternalIds(doi="10.1/abc"), provider="openalex")
    d2 = Document("Paper A", external_ids=ExternalIds(doi="10.1/abc"), provider="crossref")
    
    cluster = DocumentCluster(
        cluster_id=1,
        representative=d1,
        members=[d1, d2]
    )
    
    assert cluster.size == 2
    assert cluster.confidence == 1.0
    assert d1 in cluster.members
    assert d2 in cluster.members
```

### 🟡 Lesson Milestone Target Test (Target Implementation)

```python
def test_document_cluster_extended_milestone():
    d1 = Document("Paper A", external_ids=ExternalIds(doi="10.1/abc"), provider="openalex")
    d2 = Document("Paper A", external_ids=ExternalIds(doi="10.1/abc"), provider="crossref")
    
    # In target milestone:
    # cluster = DocumentCluster(cluster_id=1, representative=d1, members=[d1, d2],
    #                           all_dois=["10.1/abc"], provider_counts={"openalex": 1, "crossref": 1},
    #                           match_method="exact_doi")
    # assert cluster.match_method == "exact_doi"
```

---

## 5. AI Build Prompt

```text
Enhance DocumentCluster in scholar_search.models from baseline v0.1.0 to the Lesson 2.4 target milestone.
Add aggregated DOIs, arXiv IDs, provider counts, and explicit match_method tracking.
Ensure non-destructive clustering preserving all original document fields.
Add unit tests in tests/test_models.py.
```
