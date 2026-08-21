# Episode 16: Multi-Provider Deduplication & Metadata Merging

**Objective:** Combine multi-source duplicate records non-destructively and synthesize complete canonical representations.

## Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | Clean literature sets require smart deduplication without data loss. | *Show Title Slide.* |
| 2 | **Episode Goal** | Group identical records across databases and merge rich metadata into the representative record. | *Highlight goal.* |
| 3 | **Two-Phase Matching** | Phase 1 matches exact persistent IDs; Phase 2 matches normalized fuzzy titles with year gating. | *Show flowchart.* |
| 4 | **Smart Metadata Synthesis** | Combines PubMed MeSH terms, Semantic Scholar AI summaries, and OpenAlex citations. | *Show merging table.* |
| 5 | **Implementation** | Walkthrough of `src/scholar_search/dedup.py`. | *Transition to code.* |
| 6 | **Verification** | Run deduplication metadata merging tests. | *Transition to Terminal.* |

## Terminal & Code Walkthrough

1. **Show `dedup.py`**:
   - Open `src/scholar_search/dedup.py`.
   - Walk through `deduplicate()` and `_merge_metadata()`.
2. **Run the Tests**:
   - Run: `pytest tests/test_dedup.py`
   - Confirm tests pass.
