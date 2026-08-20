# Lesson 8.1: The CLI as an Agent Tool & Manifests (`cli/`)

**Status**: 🟢 **[🟢 Implemented v0.1.0]** (Baseline `deduplicate` in `cli.py`) / 🟡 **[🟡 Lesson Milestone Target]** (Full Subcommand Suite)

---

## 1. Scientific Motivation & Context

A scholarly search toolkit must be usable interactively by researchers in the terminal, non-interactively in automated pipelines, and programmatically by AI agents. Every execution should write persistent, machine-readable run manifests (`metadata.json` / `SearchManifest`) and optionally systematic review flow counts (`prisma_counts.json`) to guarantee research reproducibility.

---

## 2. Implementation Tiers

### 🟢 Baseline Implementation (`v0.1.0`)

* **Source Location**: `src/scholar_search/cli.py`
* **Available Command**: `scholar-search deduplicate <titles...>`
* **Behavior**: Reads titles from arguments, runs `Deduplicator().deduplicate()`, and prints summary string `documents=N unique=M`.

### 🟡 Lesson Milestone Target

* **`scholar-search search`**: Queries enabled providers with parameter overrides (`--year-min`, `--max-results`) and writes `SearchManifest`.
* **`scholar-search deduplicate`**: Clusters records from search output files and generates deduplication statistics.
* **`scholar-search export`**: Converts search/cluster artifacts to BibTeX, CSV, JSONL, or RIS.
* **`scholar-search validate`**: Verifies query syntax and configuration files.

---

## 3. Explicit Component Contract (Lesson Milestone Target)

### 3.1 Search Execution Manifest (`metadata.json` / `SearchManifest`)

```json
{
  "run_id": "run_2026-08-19_143000",
  "timestamp": "2026-08-19T14:30:00.000000Z",
  "queries": [
    {"id": "Q01", "text": "machine learning AND healthcare"}
  ],
  "providers": ["openalex", "crossref", "arxiv"],
  "config": {"year_min": 2020, "year_max": 2024, "max_results": 500},
  "results": {"openalex": 480, "crossref": 500, "arxiv": 210}
}
```

### 3.2 PRISMA 2020 Flow Diagram Counts (`prisma_counts.json` - Optional Review Reporting)

```json
{
  "identification": {
    "total_records": 1190,
    "records_by_provider": {"openalex": 480, "crossref": 500, "arxiv": 210}
  },
  "screening": {
    "records_after_deduplication": 890,
    "duplicates_removed": 300
  }
}
```

---

## 4. Verification & Falsifying Tests

### 🟢 Baseline Verification Test (Current Implementation)

```python
from click.testing import CliRunner
from scholar_search.cli import main

def test_cli_baseline_deduplicate_command():
    runner = CliRunner()
    result = runner.invoke(main, ["deduplicate", "Paper A", "Paper A", "Paper B"])
    assert result.exit_code == 0
    assert "documents=3 unique=2" in result.output
```

---

## 5. AI Build Prompt

```text
Expand scholar_search/cli.py from the baseline v0.1.0 to the Lesson 8.1 subcommand suite target.
Support search, deduplicate, export, and validate commands with machine-readable JSON metadata.json search manifests and optional PRISMA count exports.
Add unit tests in tests/test_cli.py.
```
