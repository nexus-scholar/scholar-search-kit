# Episode 6: Clusters & Non-Destructive Merging (`DocumentCluster`)

**Objective:** Implement non-destructive clustering of duplicate records to preserve full scientific evidence trails.

## Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | What happens when the same paper is returned by OpenAlex, PubMed, and Crossref? | *Show Title Slide.* |
| 2 | **Episode Goal** | Naive deduplication drops records permanently. We group duplicates non-destructively into clusters. | *Highlight goal.* |
| 3 | **The `DocumentCluster`** | A cluster holds a canonical `representative` (with merged metadata) and the complete list of `members`. | *Show cluster diagram.* |
| 4 | **Confidence Metrics** | Identifiers (DOI, PMID, arXiv) yield confidence `1.0`; title fuzzy matching yields `0.95`. | *Explain confidence metric.* |
| 5 | **Implementation** | We define `DocumentCluster` with derived properties `size` and `confidence`. | *Transition to code.* |
| 6 | **Verification** | We run our clustering unit tests. | *Transition to Terminal.* |

## Terminal & Code Walkthrough

1. **Show `models.py`**:
   - Open `src/scholar_search/models.py`.
   - Walk through `DocumentCluster`, highlighting `representative` vs `members`.
2. **Show Confidence Scoring**:
   - Explain how `confidence` dynamically inspects member identifier presence.
3. **Run the Tests**:
   - Run: `pytest tests/test_models.py -k "test_document_cluster"`
   - Confirm test passes.
