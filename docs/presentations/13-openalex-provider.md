# Episode 13: Ingesting OpenAlex & Citation Snowballing

**Objective:** Ingest the 250M-paper OpenAlex graph with cursor pagination, inverted index decompression, and snowballing.

## Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | Tapping into 250M+ scholarly works on OpenAlex. | *Show Title Slide.* |
| 2 | **Episode Goal** | Query OpenAlex at scale with cursor pagination and traverse citation networks. | *Highlight goal.* |
| 3 | **Cursor Pagination** | Using `cursor=*` to stream results reliably without deep offset limits. | *Show pagination flow.* |
| 4 | **Abstract Reconstruction** | Rebuilding abstracts from word position inverted indices. | *Show Python code.* |
| 5 | **Snowballing** | Traversing forward citations (`cites:...`) and backward references. | *Show snowballing diagram.* |
| 6 | **Verification** | Run OpenAlex provider tests. | *Transition to Terminal.* |

## Terminal & Code Walkthrough

1. **Show `openalex.py`**:
   - Open `src/scholar_search/providers/openalex.py`.
   - Walk through `_extract_abstract()`, `search()`, `get_citations()`, and `get_references()`.
2. **Run the Tests**:
   - Run: `pytest tests/test_providers.py -k "test_openalex"`
