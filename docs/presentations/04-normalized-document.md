# Episode 4: The Normalized Document & Author Model

**Objective:** Define the central schemas that all provider responses map into, enforcing strict data boundaries and provenance.

## Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | Now we define the core entity of our system: the canonical Document. | *Show Title Slide.* |
| 2 | **Episode Goal** | Never let raw provider JSON leak into downstream business logic. Establish a normalization boundary. | *Highlight goal.* |
| 3 | **The Canonical Schema** | We define `Author` and `Document` with provenance fields (`provider`, `provider_id`, `query_id`, `retrieved_at`). | *Point to schema diagram.* |
| 4 | **Enriched Metadata** | The model supports MeSH terms from PubMed, citation intents from Semantic Scholar, and Open Access URLs. | *Explain metadata fields.* |
| 5 | **Implementation: UTC Timestamps** | Auditability is crucial for scientific reproducibility. `mark_retrieved()` records UTC timestamps. | *Explain `mark_retrieved` method.* |
| 6 | **Verification** | Let's inspect `models.py` and run our model initialization tests. | *Transition to Terminal.* |

## Terminal & Code Walkthrough

1. **Show `models.py`**:
   - Open `src/scholar_search/models.py`.
   - Walk through the `Author` and `Document` dataclasses.
2. **Show Provenance Fields**:
   - Highlight `provider_id`, `query_id`, and `retrieved_at`.
3. **Run the Tests**:
   - Run: `pytest tests/test_models.py -k "test_author or test_document_defaults"`
   - Confirm all tests pass.
