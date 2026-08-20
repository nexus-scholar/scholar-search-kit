# Lesson 4.2: Response Normalization Subsystem (`normalizer.py`)

## 1. Scientific Motivation & Context
Heterogeneous raw API responses contain deeply nested structures, inverted indexes, diverse date serialization conventions, and various author naming formats. To maintain data integrity without crashing on unexpected API payload variations, extraction must be defensive, type-safe, and capable of resolving dot-separated paths.

## 2. Reference Architecture Analysis
* **Reference Source**: `strategy-pipeline/src/slr/providers/normalizer.py`
* **Components**:
  * `FieldExtractor`: Dot-path traversal (`"authors.0.name"`), type casting (`get_string`, `get_int`, `get_list`), and fallback paths (`get_first`).
  * `AuthorParser`: Parses `"Last, First"`, `"First Last"`, and dict authorships with ORCID extraction.
  * `DateParser`: Extracts 4-digit years from integers, date dictionaries, and ISO date strings.
  * `IDExtractor`: Extracts and normalizes DOIs, arXiv IDs, PMIDs, OpenAlex IDs, and S2 Corpus IDs.
  * `ResponseNormalizer`: High-level coordinator mapping raw response dicts to `Document` objects.

## 3. Explicit Component Contract

### 3.1 `FieldExtractor`
* `get(path: str, default: Any = None) -> Any`: Traverses nested dicts and list indices via dot notation (e.g. `primary_location.source.display_name`).
* `get_string(path: str, default: str = "") -> str`: Returns trimmed string or default.
* `get_int(path: str, default: Optional[int] = None) -> Optional[int]`: Converts to `int` safely, logging warning on failure.
* `get_first(*paths: str, default: Any = None) -> Any`: Returns the first non-None value encountered across multiple candidate paths.

### 3.2 `AuthorParser`
* `parse_author_name(name: str) -> Dict[str, Optional[str]]`: Splits `"Last, First"` or `"First Last"` into `family` and `given` components.
* `parse_authors(authors_data: List[Any], ...) -> List[Author]`: Maps raw author lists or string arrays into typed `Author` models.

### 3.3 `DateParser`
* `extract_year(date_value: Any) -> Optional[int]`:
  * If `int`: Validates $1900 \le year \le 2100$.
  * If `dict`: Checks keys `"year"`, `"Year"`, or nested `"date-parts"`.
  * If `str`: Uses regex `\b(19|20)\d{2}\b` to extract 4-digit year.

## 4. Verification & Falsifying Tests

```python
from scholar_search.providers.normalizer import FieldExtractor, AuthorParser, DateParser

def test_field_extractor_nested_paths():
    data = {
        "metadata": {
            "source": {"name": "Journal of AI"},
            "counts": [10, 20, 30]
        }
    }
    extractor = FieldExtractor(data)
    assert extractor.get_string("metadata.source.name") == "Journal of AI"
    assert extractor.get_int("metadata.counts.1") == 20
    assert extractor.get("metadata.missing.path", default="fallback") == "fallback"

def test_author_parser_formats():
    assert AuthorParser.parse_author_name("Knuth, Donald E.") == {
        "family": "Knuth", "given": "Donald E."
    }
    assert AuthorParser.parse_author_name("Donald E. Knuth") == {
        "family": "Knuth", "given": "Donald E."
    }

def test_date_parser_formats():
    assert DateParser.extract_year("2023-05-15T12:00:00Z") == 2023
    assert DateParser.extract_year({"year": 2021}) == 2021
    assert DateParser.extract_year(1850) is None  # Out of range bound
```

## 5. AI Build Prompt

```text
Implement FieldExtractor, AuthorParser, DateParser, IDExtractor, and ResponseNormalizer in scholar_search/providers/normalizer.py following Lesson 4.2.
Provide defensive type-safe getters, dot-path traversal, author name splitting, date extraction, and ID normalization.
Add unit tests in tests/test_normalizer.py.
```
