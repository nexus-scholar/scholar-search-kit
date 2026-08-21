# Episode 19: End-to-End Pipeline & Integration

**Objective:** Demonstrate an end-to-end research workflow from discovery to verification, deduplication, and export.

## Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | Assembling all components into a production literature discovery pipeline. | *Show Title Slide.* |
| 2 | **Episode Goal** | Run a complete workflow: query 6 providers, deduplicate records, verify citations, and export to JSON/PDF-kit. | *Highlight goal.* |
| 3 | **Architecture in Action** | HTTP Client $\rightarrow$ Translators $\rightarrow$ Providers $\rightarrow$ Deduplicator $\rightarrow$ Verifier $\rightarrow$ Exporter. | *Show full architecture diagram.* |
| 4 | **Downstream Interop** | Piping JSON output directly into `scholar-pdf-kit` for automatic open-access PDF downloads. | *Show PDF-kit integration.* |
| 5 | **Implementation** | Python API walkthrough. | *Transition to code.* |
| 6 | **Verification** | Execute full test suite (`pytest`). | *Transition to Terminal.* |

## Terminal & Code Walkthrough

1. **Demonstrate Python API**:
   - Write a short script importing `SearchEngine`, `Deduplicator`, and `Exporter`.
2. **Run Full Pytest Suite**:
   - Run: `pytest -v`
   - Show all tests passing.
