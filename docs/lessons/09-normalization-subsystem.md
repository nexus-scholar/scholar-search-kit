# Lesson 4.2: Response Normalization Subsystem

## 1. Scientific Motivation & Context
Heterogeneous API responses represent author names, publication dates, abstracts, and identifiers in conflicting formats. Normalization ensures that downstream consumers (deduplicators, verifiers, RAG indexers, BibTeX exporters) receive clean, validated, and uniform `Document` structures.

---

## 2. Ingestion Normalization Rules

### 2.1 Author Name Parsing
- Authors provided as unstructured strings (`"Alan M. Turing"`) are parsed into `family_name="Turing"` and `given_name="Alan M."`.
- Structured authors (Crossref/OpenAlex with `given` and `family`) map directly.
- Single-name entities (e.g. `"Aristotle"`, `"CERN Collaboration"`) populate `family_name` while keeping `given_name=None`.

### 2.2 Date & Year Normalization
- Extracts standard 4-digit integers ($1900 \le \text{year} \le 2100$).
- Parses diverse timestamp formats (ISO-8601, RFC-3339, Crossref `date-parts` `[[2023, 5, 12]]`, PubMed XML `<PubDate>`).
- If unparseable or absent, defaults safely to `None` without falsifying publication timelines.

### 2.3 Abstract Cleansing
- Reassembles OpenAlex inverted indexes into continuous prose.
- Strips XML/HTML tags (e.g. `<b>`, `<i>`, `<p>`, `<jats:p>`).
- Cleanses non-printable control characters and normalizes Unicode whitespace.

---

## 3. Verification & Automated Tests

```python
from scholar_search.models import Author, Document


def test_author_normalization():
    a = Author(family_name="Knuth", given_name="Donald E.")
    assert a.full_name == "Donald E. Knuth"
    assert a.family_name == "Knuth"
```
