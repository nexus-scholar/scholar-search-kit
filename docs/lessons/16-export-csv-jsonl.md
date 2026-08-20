# Lesson 7.1: Exporting to CSV, JSON & JSONL (`export/`)

## 1. Scientific Motivation & Context
Search results must be shared with collaborators, imported into statistical software (R, Pandas, SPSS), or piped into screening and natural language processing pipelines. Exporters must write standard tabular (CSV) and semi-structured (JSON/JSONL) formats deterministically without mutating source models or dropping provenance attributes.

## 2. Reference Architecture Analysis
* **Reference Sources**:
  * `strategy-pipeline/src/slr/export/base.py`
  * `strategy-pipeline/src/slr/export/csv_exporter.py`
  * `strategy-pipeline/src/slr/export/jsonl_exporter.py`
* **Components**:
  * `BaseExporter`: Handles output directory resolution and file extensions.
  * `CSVExporter`: Flattens authors and external IDs into columns; supports `"representatives"` mode (with cluster summary columns) and `"all"` mode.
  * `JSONLExporter` / `JSONExporter`: Stream-friendly line-by-line JSON serialization and standard JSON array output.

## 3. Explicit Component Contract

### 3.1 `CSVExporter`
* **Standard Columns**:
  `title`, `year`, `authors`, `author_count`, `venue`, `abstract`, `provider`, `provider_id`, `doi`, `arxiv_id`, `pubmed_id`, `openalex_id`, `s2_id`, `url`, `language`, `cited_by_count`, `query_id`, `query_text`, `retrieved_at`, `cluster_id`.
* **Cluster Summary Columns** (when exporting representatives):
  `cluster_size`, `cluster_confidence`, `cluster_dois`, `cluster_arxiv_ids`, `cluster_providers`.

### 3.2 `JSONLExporter`
* **Modes**:
  * `"representatives"`: Writes one line per cluster representative document with embedded `cluster_metadata`.
  * `"all"`: Writes one line per document member.
  * `"clusters"`: Writes full `DocumentCluster` objects including the `members` list.

## 4. Verification & Falsifying Tests

```python
from pathlib import Path
from scholar_search.export import Exporter
from scholar_search.models import Document, ExternalIds

def test_csv_and_jsonl_export(tmp_path: Path):
    docs = [
        Document("Study A", year=2020, external_ids=ExternalIds(doi="10.1/a")),
        Document("Study B", year=2021, external_ids=ExternalIds(doi="10.1/b")),
    ]
    exporter = Exporter()
    
    csv_file = exporter.csv(docs, tmp_path / "out.csv")
    jsonl_file = exporter.jsonl(docs, tmp_path / "out.jsonl")
    
    assert csv_file.exists()
    assert jsonl_file.exists()
    assert len(jsonl_file.read_text(encoding="utf-8").strip().splitlines()) == 2
```

## 5. AI Build Prompt

```text
Implement BaseExporter, CSVExporter, and JSONLExporter in scholar_search/export.py following Lesson 7.1.
Support flattened CSV columns, cluster summary metadata, streamable JSONL output, and automatic directory creation.
Add unit tests in tests/test_export.py.
```
