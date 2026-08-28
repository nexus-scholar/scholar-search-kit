# Ingestion, Export, and Pipeline Integration

This guide details supported file formats, importers, exporters, and downstream pipeline workflows (such as connecting with `scholar-pdf-kit` and `scholar-rag-kit`).

---

## 1. Supported File Formats

| Format | Importer Class | Exporter Method | Notes |
| :--- | :--- | :--- | :--- |
| **JSON** | `JSONImporter` | `Exporter.json(...)` | Standard JSON array of serialized `Document` records. Default interchange format. |
| **JSONL** | `JSONLImporter` | `Exporter.jsonl(...)` | Line-delimited JSON. Recommended for streaming large corpora. |
| **RIS** | `RISImporter` | — | Standard citation export format from Zotero, Mendeley, EndNote, and Google Scholar. |
| **CSV** | — | `Exporter.csv(...)` | Tabular export containing `title`, `year`, `provider`, `doi`, `arxiv_id`, `pubmed_id`, `venue`, `citations_count`. |

---

## 2. CLI Format Conversion & Import

```bash
# Convert an RIS library export to standardized JSON
uv run scholar-search export my_library.ris papers.json --format json

# Convert a JSON dataset to CSV for spreadsheet inspection
uv run scholar-search export papers.json papers.csv --format csv

# Import RIS directly with verification and metadata enrichment
uv run scholar-search import zotero_export.ris --verify --enrich --output verified.json
```

---

## 3. Pipeline Integration with `scholar-pdf-kit`

`scholar-search-kit` and `scholar-pdf-kit` form a sequential discovery-to-download pipeline:

```bash
# Step 1: Discover & deduplicate literature with scholar-search-kit
uv run scholar-search search "retrieval augmented generation" --limit 20 --output literature.json

# Step 2: Bulk download Open Access PDFs using scholar-pdf-kit
uv run scholar-pdf --input literature.json --output downloaded_pdfs/
```

### Programmatic Python Pipeline Handoff

```python
from pathlib import Path
from scholar_search import Exporter, Document

def save_for_pdf_kit(documents: list[Document], destination: Path) -> Path:
    """Exports Document instances to standardized JSON consumable by AsyncPDFDownloader."""
    exporter = Exporter()
    return exporter.json(documents, destination)
```
