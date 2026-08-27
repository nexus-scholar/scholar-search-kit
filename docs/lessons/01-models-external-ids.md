# Lesson 2.1: Persistent Identifiers (`ExternalIds`)

## 1. Scientific Motivation & Context
In scholarly research, works are indexed across multiple disparate databases (Crossref, PubMed, arXiv, OpenAlex, Semantic Scholar). Each provider formats identifiers differently (e.g. `https://doi.org/10.1234/X`, `doi:10.1234/x`, `10.1234/X`). Without strict normalization, identity comparisons fail, leading to:
1. **False Negatives (Missed Duplicates)**: The same paper retrieved from Crossref and arXiv is counted twice, inflating research review counts.
2. **False Positives (Erroneous Merges)**: Malformed or empty IDs collide, collapsing distinct studies.

---

## 2. Component Contract & Implementation

* **Module**: `scholar_search.models`
* **Dataclass**: `ExternalIds`

```python
from dataclasses import dataclass


@dataclass
class ExternalIds:
    doi: str | None = None
    arxiv_id: str | None = None
    pubmed_id: str | None = None
    openalex_id: str | None = None
    s2_id: str | None = None

    def __post_init__(self) -> None:
        if self.doi:
            value = self.doi.strip().lower()
            for prefix in (
                "https://doi.org/",
                "http://doi.org/",
                "https://dx.doi.org/",
                "http://dx.doi.org/",
                "doi:",
            ):
                if value.startswith(prefix):
                    value = value[len(prefix) :]
            value = value.strip()
            self.doi = value if value else None
        else:
            self.doi = None

        if self.arxiv_id:
            val = self.arxiv_id.strip()
            for prefix in ("arxiv:", "arXiv:"):
                if val.startswith(prefix):
                    val = val[len(prefix) :]
            val = val.strip()
            self.arxiv_id = val if val else None
```

---

## 3. Invariants & Normalization Rules

1. **Case-Insensitive DOI**: All valid DOIs are converted to lowercase.
2. **Comprehensive Prefix Stripping**: URL wrappers (`https://doi.org/`, `http://dx.doi.org/`) and URN prefixes (`doi:`, `DOI:`) are cleanly removed.
3. **Blank & Whitespace Cleansing**: Empty strings (`""`) and whitespace (`"   "`) convert strictly to `None`.
4. **arXiv Normalization**: Leading `arxiv:` prefixes are stripped.
5. **No Identifier Cross-Contamination**: DOIs, arXiv IDs, PMIDs, OpenAlex IDs, and S2 IDs remain isolated in their respective typed fields.

---

## 4. Verification & Automated Tests

Run with `pytest tests/test_models.py -k "test_external_ids"`:

```python
from scholar_search.models import ExternalIds


def test_external_ids_normalization():
    cases = [
        ("https://doi.org/10.1000/182", "10.1000/182"),
        ("http://doi.org/10.1000/182", "10.1000/182"),
        ("DOI:10.1000/182", "10.1000/182"),
        ("doi: 10.1000/182", "10.1000/182"),
        ("10.1000/182", "10.1000/182"),
        ("HTTPS://DOI.ORG/10.1000/ABC", "10.1000/abc"),
    ]
    for raw, expected in cases:
        ids = ExternalIds(doi=raw)
        assert ids.doi == expected
```
