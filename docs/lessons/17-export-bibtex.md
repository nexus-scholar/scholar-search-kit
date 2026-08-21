# Lesson 7.2: Exporting to BibTeX for Citation Managers (`export.py`)

## 1. Scientific Motivation & Context
Researchers manage references using citation managers (Zotero, Mendeley, JabRef) and write papers directly in LaTeX. To integrate into academic workflows, the search toolkit generates clean BibTeX entries with valid cite keys, author formatting, and LaTeX escaping.

---

## 2. Invariants & Citation Key Formatting

1. **Cite Key Algorithm**: Combines first author family name, publication year, and significant title keyword (e.g. `Vaswani2017Attention`).
2. **Author Formatting**: Separates multiple authors with standard `and` keywords.
3. **LaTeX Escaping**: Safely escapes special symbols (`&`, `%`, `$`, `#`, `_`).
4. **Preprint Support**: Injects `eprint = {arxiv_id}` and `archivePrefix = {arXiv}` for preprints.
