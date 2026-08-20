# Lesson 2.1: Persistent Identifiers (`ExternalIds`)

## 1. Scientific Motivation & Context
In scholarly research, works are indexed across multiple disparate databases (Crossref, PubMed, arXiv, OpenAlex, Semantic Scholar). Each provider formats identifiers differently (e.g. `https://doi.org/10.1234/X`, `doi:10.1234/x`, `10.1234/X`). Without strict normalization, identity comparisons fail, leading to either:
1. **False Negatives (Missed Duplicates)**: The same paper retrieved from Crossref and arXiv is counted twice, inflating research review counts.
2. **False Positives (Erroneous Merges)**: Malformed or empty IDs collide, collapsing distinct studies.

## 2. Reference Architecture Analysis
* **Reference Source**: `strategy-pipeline/src/slr/core/models.py::ExternalIds`
* **Observed Behavior**:
  * Pydantic model with field validator on `doi`.
  * Regex stripping: `re.sub(r"^https?://(dx\.)?doi\.org/", "", v, flags=re.IGNORECASE)` and `re.sub(r"^doi:\s*", "", v, flags=re.IGNORECASE)`.
  * Trims whitespace and lowercases the normalized string.

## 3. Explicit Component Contract

### Class Definition: `ExternalIds`
* **Module**: `scholar_search.models` (or `slr.core.models`)
* **Attributes**:
  * `doi`: `Optional[str] = None`
  * `arxiv_id`: `Optional[str] = None`
  * `pubmed_id`: `Optional[str] = None`
  * `openalex_id`: `Optional[str] = None`
  * `s2_id`: `Optional[str] = None`

### Invariants & Validation Rules
1. **Case-Insensitive DOI**: All valid DOIs must be converted to lowercase.
2. **Prefix Stripping**: URL prefixes (`https://doi.org/`, `http://doi.org/`, `http://dx.doi.org/`, `https://dx.doi.org/`) and URN prefixes (`doi:`, `DOI:`) MUST be stripped.
3. **No Fake Identifiers**: Empty strings (`""`), whitespace strings (`"   "`), or placeholder strings (`"none"`, `"null"`) must be converted to `None`.
4. **arXiv ID Cleansing**: Leading `arxiv:` or `arXiv:` prefixes must be removed.
5. **Distinct Repositories**: Identifiers from different systems must remain separate fields; never overload `doi` with an arXiv ID or S2 Corpus ID.

## 4. Edge Cases & Counterexamples
| Input DOI | Expected Normalized DOI | Why Naive Implementations Fail |
| :--- | :--- | :--- |
| `"https://doi.org/10.1145/3377811.3380321"` | `"10.1145/3377811.3380321"` | Fails if only checking for `doi:` prefix |
| `"http://dx.doi.org/10.1016/J.JSS.2020.110592"` | `"10.1016/j.jss.2020.110592"` | Fails if uppercase or `dx.` is not stripped |
| `"DOI: 10.1000/182"` | `"10.1000/182"` | Fails if space after `DOI:` is not handled |
| `""` or `"   "` | `None` | Fails if empty string is kept, causing fake matches |
| `None` | `None` | Must not throw AttributeError |

## 5. Verification & Falsifying Tests

```python
import pytest
from scholar_search.models import ExternalIds

def test_doi_normalization_variations():
    cases = [
        ("https://doi.org/10.1000/182", "10.1000/182"),
        ("http://dx.doi.org/10.1000/182", "10.1000/182"),
        ("DOI:10.1000/182", "10.1000/182"),
        ("doi: 10.1000/182", "10.1000/182"),
        ("10.1000/182", "10.1000/182"),
        ("HTTPS://DOI.ORG/10.1000/ABC", "10.1000/abc"),
    ]
    for raw, expected in cases:
        ids = ExternalIds(doi=raw)
        assert ids.doi == expected

def test_empty_doi_becomes_none():
    assert ExternalIds(doi="").doi is None
    assert ExternalIds(doi="   ").doi is None
    assert ExternalIds(doi=None).doi is None
```

## 6. AI Build Prompt

```text
Implement ExternalIds in scholar_search.models following the Lesson 2.1 contract.
Normalize all variations of DOIs (stripping http/https/dx.doi.org and doi: prefixes, trimming, and lowercasing).
Convert blank strings to None.
Ensure arXiv IDs strip leading 'arxiv:' prefixes.
Add full unit tests in tests/test_models.py.
```
