# Lesson 6.1: Deduplication & Conservative Matching (`dedup/`)

**Status**: 🟢 **Implemented (Baseline v0.1.0 in `dedup.py`)** / 🟡 **4-Phase Strategy Target**

---

## 1. Scientific Motivation & Context
When aggregating literature from multiple databases, duplicate records appear frequently (e.g. preprints vs published papers, Crossref DOI records vs OpenAlex works). Deduplication precision is paramount:
* **False Merges (High Scientific Risk)**: Erroneously collapsing two distinct papers with similar titles permanently deletes evidence.
* **Missed Merges**: Inflates review counts and forces duplicate human screening.

---

## 2. Implementation Tiers

### 🟢 Current Baseline Implementation (`v0.1.0`)
* Located in `src/scholar_search/dedup.py`.
* **Mechanism**:
  1. Checks exact matching on `external_ids.doi` or `external_ids.arxiv_id`.
  2. If no identifier match, checks conservative title similarity via Python `difflib.SequenceMatcher.ratio() >= 0.97` on alphanumeric lowercased strings.
  3. Appends document to matching cluster or creates new cluster.
  4. Computes total, unique, and duplicate count statistics.

### 🟡 Target Milestone: 4-Phase Conservative Algorithm
* Expands the baseline into multi-phase candidate indexing and publication year gap gating:
  1. **Phase 1 (Exact DOI Index)**: Merges all unclustered records sharing identical normalized DOI (`confidence = 1.0`, `match_method = "exact_doi"`).
  2. **Phase 2 (Exact arXiv ID Index)**: Merges all remaining unclustered records sharing identical arXiv ID (`confidence = 1.0`, `match_method = "exact_arxiv_id"`).
  3. **Phase 3 (Fuzzy Title + Year Gap Gating)**: Merges remaining unclustered records matching on normalized title if $|year_1 - year_2| \le \text{max\_year\_gap}$ (default: $1$) (`confidence = 0.95`, `match_method = "fuzzy_title"`).
  4. **Phase 4 (Singletons)**: Assigns all remaining unique records to singleton clusters.
* **Representative Document Scoring Formula**:
  $$\text{Score}(d) = \Big( \text{Completeness}(d),\ \text{Citations}(d),\ \text{ProviderPriority}(d) \Big)$$
  * $\text{Completeness}(d) = 10 \cdot \mathbb{I}(\text{abstract}) + 5 \cdot \mathbb{I}(\text{authors}) + 3 \cdot \mathbb{I}(\text{venue}) + 2 \cdot \mathbb{I}(\text{doi})$
  * $\text{ProviderPriority}$: Crossref (4) > OpenAlex (3) > Semantic Scholar (2) > arXiv (1) > Unknown (0).

---

## 3. Verification & Falsifying Tests

```python
from scholar_search.dedup import Deduplicator
from scholar_search.models import Document, ExternalIds

def test_dedup_doi_and_title_phases():
    d1 = Document("Deep Residual Learning", year=2016, external_ids=ExternalIds(doi="10.1109/CVPR.2016.90"))
    d2 = Document("Deep Residual Learning", year=2015, external_ids=ExternalIds(arxiv_id="1512.03385"))
    d3 = Document("Deep Residual Learning", year=2016, external_ids=ExternalIds(doi="10.1109/cvpr.2016.90"))
    
    clusters = Deduplicator().deduplicate([d1, d2, d3])
    
    # d1 and d3 merge on DOI
    assert len(clusters) <= 2
    doi_cluster = next(c for c in clusters if d1 in c.members and d3 in c.members)
    assert doi_cluster.size == 2
```

---

## 4. AI Build Prompt

```text
Enhance Deduplicator in scholar_search/dedup.py from the baseline v0.1.0 to the Lesson 6.1 4-phase target milestone.
Implement candidate indexing (exact DOI -> exact arXiv -> fuzzy title with max_year_gap <= 1 -> singletons).
Implement lexicographic representative scoring tuple.
Add unit tests in tests/test_dedup.py.
```
