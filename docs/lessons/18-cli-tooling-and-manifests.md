# Lesson 8.1: Modern Typer CLI & Workflow Automation (`cli.py`)

## 1. Scientific Motivation & Context
A scholarly search toolkit must be usable interactively by researchers in the terminal, non-interactively in automated batch pipelines, and programmatically by AI coding agents.

Our modern **Typer** CLI provides rich formatting, progress spinners, multi-provider execution, and verification pipelines.

---

## 2. CLI Command Suite

```bash
# 1. Multi-provider federated search
scholar-search search "quantum computing" --providers openalex,crossref,arxiv --limit 20 --output results.json

# 2. Forward & backward citation snowballing
scholar-search snowball W2741809807 --direction forward --limit 50 --output citing_papers.json

# 3. Import legacy files with verification and OpenAlex hydration
scholar-search import legacy_citations.ris --verify --enrich --output verified.json

# 4. Standalone deduplication
scholar-search dedup search_results.json --output deduped.json

# 5. Format conversion
scholar-search export search_results.json --output summary.csv --format csv
```

---

## 3. Verification & Automated Tests

Run with `pytest tests/test_cli.py`:

```python
from typer.testing import CliRunner
from scholar_search.cli import app


def test_cli_search():
    runner = CliRunner()
    result = runner.invoke(app, ["search", "deep learning", "--limit", "3", "--quiet"])
    assert result.exit_code == 0
```
