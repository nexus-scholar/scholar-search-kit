# Episode 18: File I/O, Exporters & Importers

**Objective:** Ingest and export scholarly data across JSON, JSONL, CSV, and RIS formats.

## Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | Seamless data movement across the research tool ecosystem. | *Show Title Slide.* |
| 2 | **Episode Goal** | Ingest legacy citation files and export structured datasets for downstream analysis. | *Highlight goal.* |
| 3 | **Supported Formats** | Standard JSON arrays, streaming JSONL, flattened CSV, and RIS bibliographies. | *Show format grid.* |
| 4 | **Verified Ingestion** | The `import` command can verify records against Crossref and hydrate missing fields on the fly. | *Explain verification pipeline.* |
| 5 | **Implementation** | Walkthrough of `export.py` and `importers.py`. | *Transition to code.* |
| 6 | **Verification** | Run roundtrip export-import tests. | *Transition to Terminal.* |

## Terminal & Code Walkthrough

1. **Show `export.py` and `importers.py`**:
   - Walk through `Exporter` methods and `RISImporter` parsing.
2. **Run Tests**:
   - Run: `pytest tests/test_importers_exporters.py`
