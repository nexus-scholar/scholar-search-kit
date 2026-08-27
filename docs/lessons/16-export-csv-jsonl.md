# Lesson 7.1: Exporting & Importing JSON, JSONL, CSV & RIS (`export.py` & `importers.py`)

## 1. Scientific Motivation & Context
Search results must easily feed downstream tools in the research pipeline (such as `scholar-pdf-kit`, `scholar-rag-kit`, or reference managers like Zotero and EndNote). Standardized export and import formats ensure seamless interoperability.

---

## 2. Component Contract & Implementation

* **Module**: `scholar_search.export` & `scholar_search.importers`
* **Classes**: `Exporter`, `RISImporter`, `JSONImporter`, `JSONLImporter`

### 2.1 Exporters (`Exporter`)
- `exporter.json(documents, path)`: Standard JSON array containing serialized documents and persistent identifiers.
- `exporter.jsonl(documents, path)`: Streamable line-delimited JSON for high-throughput batch processing.
- `exporter.csv(documents, path)`: Flattened tabular format with extracted DOIs, PMIDs, authors, and venues.

### 2.2 Importers
- `RISImporter.import_file(path)`: Parses standard academic `.ris` citation files (`TI`, `AU`, `PY`, `DO`, `AB`, `JO`).
- `JSONImporter.import_file(path)`: Ingests structured JSON arrays into `Document` objects.
- `JSONLImporter.import_file(path)`: Streams `.jsonl` files into `Document` objects.

---

## 3. Verification & Automated Tests

Run with `pytest tests/test_importers_exporters.py`:

```python
from pathlib import Path
from scholar_search.export import Exporter
from scholar_search.importers import JSONImporter, RISImporter
from scholar_search.models import Document, ExternalIds


def test_json_roundtrip(tmp_path: Path):
    docs = [
        Document("Study Alpha", year=2024, external_ids=ExternalIds(doi="10.1000/1"))
    ]
    out_file = tmp_path / "results.json"

    Exporter().json(docs, out_file)
    imported = JSONImporter().import_file(out_file)

    assert len(imported) == 1
    assert imported[0].title == "Study Alpha"
    assert imported[0].external_ids.doi == "10.1000/1"
```
