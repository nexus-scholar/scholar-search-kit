# Lesson 7.2: Exporting to BibTeX for Citation Managers (`export/bibtex_exporter.py`)

## 1. Scientific Motivation & Context
Researchers manage references using citation managers like Zotero, Mendeley, JabRef, and EndNote, or write papers directly in LaTeX. To integrate into academic workflows, the search toolkit must generate standard `.bib` files with valid citation keys, appropriate entry types (`@article`, `@inproceedings`, `@misc`), proper author formatting (`and` delimiter), and LaTeX special character escaping.

## 2. Reference Architecture Analysis
* **Reference Source**: `strategy-pipeline/src/slr/export/bibtex_exporter.py`
* **Components**:
  * Citation Key Generator: Emits `FirstAuthorYYYYKeyword` (e.g. `Vaswani2017Attention`).
  * Entry Type Detector: Maps conference proceedings to `@inproceedings`, journals to `@article`, preprints/arXiv to `@misc`.
  * LaTeX Escaper: Replaces reserved characters (`\`, `&`, `%`, `$`, `#`, `_`, `{`, `}`, `~`, `^`).

## 3. Explicit Component Contract

### Class Definition: `BibTeXExporter`
* **Citation Key Algorithm (`_generate_cite_key`)**:
  * First author family name (cleaned of punctuation).
  * 4-digit publication year.
  * First significant title word (skips stop words: `a, an, the, on, in, at, of, for, to, and, or`).
  * Total key length capped at 30 characters.
* **Entry Type Heuristic (`_determine_entry_type`)**:
  * If venue contains `conference, proceedings, workshop, symposium, congress` $\rightarrow$ `@inproceedings`.
  * If venue contains `journal, review, magazine, transactions` or record has DOI $\rightarrow$ `@article`.
  * If provider is `arxiv` or venue is missing $\rightarrow$ `@misc`.
* **arXiv Support**: Emits `eprint = {arxiv_id}` and `archivePrefix = {arXiv}`.

## 4. Verification & Falsifying Tests

```python
from pathlib import Path
from scholar_search.export.bibtex_exporter import BibTeXExporter
from scholar_search.models import Author, Document, ExternalIds

def test_bibtex_entry_formatting(tmp_path: Path):
    doc = Document(
        title="Attention & Transformers in 100% of Cases",
        year=2017,
        authors=[Author("Vaswani", "Ashish"), Author("Shazeer", "Noam")],
        venue="Advances in Neural Information Processing Systems Conference",
        external_ids=ExternalIds(arxiv_id="1706.03762")
    )
    exporter = BibTeXExporter(output_dir=tmp_path)
    out_file = exporter.export_documents([doc], "refs.bib")
    
    content = out_file.read_text(encoding="utf-8")
    assert "@inproceedings{Vaswani2017Attention" in content
    assert "author = {Ashish Vaswani and Noam Shazeer}" in content
    assert "\\&" in content  # Escaped ampersand
    assert "\\%" in content  # Escaped percent
    assert "eprint = {1706.03762}" in content
```

## 5. AI Build Prompt

```text
Implement BibTeXExporter in scholar_search/export/bibtex_exporter.py following Lesson 7.2.
Support citation key generation (FirstAuthorYYYYKeyword), entry type detection (@article, @inproceedings, @misc), LaTeX character escaping, and arXiv eprint tags.
Add unit tests in tests/test_bibtex_exporter.py.
```
