# Episode 5: Query as a Research Instrument (`Query`)

**Objective:** Transform search queries from raw strings into structured, reproducible research instruments.

## Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | In reproducible research, a query is not a casual string; it is a formal research instrument. | *Show Title Slide.* |
| 2 | **Episode Goal** | We need a structured `Query` object that encapsulates text, filter boundaries, language, and IDs. | *Highlight goal.* |
| 3 | **Filter Constraints** | Our model supports independent publication year bounds (`year_min`, `year_max`) and result limits. | *Show query diagram.* |
| 4 | **Traceability Linkage** | Every paper retrieved through a query gets tagged with `doc.query_id == query.id`. | *Explain provenance link.* |
| 5 | **Implementation** | We define `Query` with sensible defaults (`id="Q001"`, `language="en"`). | *Transition to code.* |
| 6 | **Verification** | We run our query unit tests verifying boundary integrity. | *Transition to Terminal.* |

## Terminal & Code Walkthrough

1. **Show `models.py`**:
   - Open `src/scholar_search/models.py`.
   - Walk through the `Query` dataclass.
2. **Show Traceability**:
   - Explain how `Document.query_id` connects directly to `Query.id`.
3. **Run the Tests**:
   - Run: `pytest tests/test_models.py -k "test_query_model"`
   - Confirm test passes.
