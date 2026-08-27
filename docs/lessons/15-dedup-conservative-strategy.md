# Lesson 6.1: Multi-Provider Deduplication & Smart Metadata Merging (`dedup.py`)

## 1. Scientific Motivation & Context
When querying federated databases, duplicate records are ubiquitous (e.g. arXiv preprints vs peer-reviewed Crossref DOIs vs PubMed citations).
A naive deduplicator discards duplicate records entirely, throwing away valuable provider-specific metadata (such as PubMed MeSH headings or Semantic Scholar AI TLDR summaries).
Our `Deduplicator` groups duplicates non-destructively and synthesizes the most complete canonical `representative` record.

---

## 2. Component Contract & Algorithm

* **Module**: `scholar_search.dedup`
* **Class**: `Deduplicator`

### 2-Phase Matching Engine
1. **Phase 1 (Persistent Identifiers)**: Matches on exact normalized `doi`, `arxiv_id`, `pubmed_id`, `openalex_id`, or `s2_id`.
2. **Phase 2 (Fuzzy Title + Year Gating)**: Matches on cleaned lowercase alphanumeric titles with `difflib.SequenceMatcher.ratio() >= 0.95` and $|year_1 - year_2| \le 1$.

### Non-Destructive Metadata Merging (`_merge_metadata`)
When a duplicate is added to an existing cluster, the representative document is dynamically enriched:
- Backfills missing `abstract`, `venue`, `year`, `url`.
- Combines distinct `authors` by ORCID/name.
- Merges `mesh_terms`, `citation_intents`, and `tldr` summaries.
- Adopts maximum `citations_count` and `references_count`.

---

## 3. Verification & Automated Tests

Run with `pytest tests/test_dedup.py`:

```python
from scholar_search.dedup import Deduplicator
from scholar_search.models import Document, ExternalIds


def test_dedup_metadata_merging():
    d1 = Document(
        title="Attention Is All You Need",
        year=2017,
        provider="arxiv",
        external_ids=ExternalIds(arxiv_id="1706.03762"),
        abstract="The dominant sequence transduction models...",
    )
    d2 = Document(
        title="Attention is All You Need",
        year=2017,
        provider="pubmed",
        external_ids=ExternalIds(arxiv_id="1706.03762"),
        mesh_terms=["Neural Networks, Computer", "Natural Language Processing"],
        citations_count=120000,
    )

    clusters = Deduplicator().deduplicate([d1, d2])
    assert len(clusters) == 1
    rep = clusters[0].representative

    assert rep.abstract is not None
    assert "Neural Networks, Computer" in rep.mesh_terms
    assert rep.citations_count == 120000
```
