# Episode 16b: Document Verification & Hallucination Detection

**Objective:** Cross-reference literature against Crossref's 150M records to detect LLM hallucinations and hydrate missing metadata.

## Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | Detecting LLM hallucinations and hydrating missing scientific metadata. | *Show Title Slide.* |
| 2 | **Episode Goal** | Never trust unverified citation strings. Validate against official registries. | *Highlight goal.* |
| 3 | **DOI & Title Verification** | Checks DOI existence on Crossref and verifies bibliographic title matches. | *Show verification diagram.* |
| 4 | **Catching Hallucinations** | Detects fake DOIs, mangled titles, and fabricated author names. | *Show hallucination catch example.* |
| 5 | **Metadata Hydration** | Backfills missing abstracts, venues, and citation counts via OpenAlex. | *Show hydration flow.* |
| 6 | **Verification** | Run verification and hydration tests. | *Transition to Terminal.* |

## Terminal & Code Walkthrough

1. **Show `verifier.py`**:
   - Open `src/scholar_search/verifier.py`.
   - Walk through `verify_document()` and `hydrate_metadata()`.
2. **Run the Tests**:
   - Run: `pytest tests/test_verifier.py`
   - Confirm verification and hallucination detection tests pass.
