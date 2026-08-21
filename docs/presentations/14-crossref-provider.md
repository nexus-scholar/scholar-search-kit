# Episode 14: Crossref & Bibliographic Validation

**Objective:** Ingest published DOIs and validate unformatted citation references against Crossref.

## Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | The definitive registry for published DOIs: Crossref. | *Show Title Slide.* |
| 2 | **Episode Goal** | Query registered publisher metadata and validate citation strings. | *Highlight goal.* |
| 3 | **Polite Pool Etiquette** | Attaching researcher email headers for fast, dedicated API rate limits. | *Show header setup.* |
| 4 | **Bibliographic Matching** | Cross-checking messy reference strings against 150M records with `validate_reference()`. | *Show matching diagram.* |
| 5 | **Implementation** | Walkthrough of `src/scholar_search/providers/crossref.py`. | *Transition to code.* |
| 6 | **Verification** | Run Crossref provider tests. | *Transition to Terminal.* |

## Terminal & Code Walkthrough

1. **Show `crossref.py`**:
   - Open `src/scholar_search/providers/crossref.py`.
   - Walk through `search()` and `validate_reference()`.
2. **Run the Tests**:
   - Run: `pytest tests/test_providers.py -k "test_crossref"`
