# Lesson 5.2: Ingesting OpenAlex at Scale (`providers/openalex.py`)

**Status**: 🟡 **Lesson Milestone Target** / 🔵 **Reference: `strategy-pipeline/src/slr/providers/openalex.py`**

---

## 1. Scientific Motivation & Context
OpenAlex is an open index of $>250\text{M}$ scholarly records. Ingesting OpenAlex requires deep cursor pagination (`cursor=*`), polite pool rate limiting with researcher contact headers, and decompressing word inverted indexes into readable abstract strings.

## 2. Staged 7-Step AI Build Checkpoints
To make AI-assisted implementation manageable and verifiable, build `OpenAlexProvider` through these 7 focused checkpoints:

1. **Step 1 (Fixture)**: Save a static mock response fixture (`fixtures/openalex_work.json`).
2. **Step 2 (Extraction)**: Implement `_extract_ids()` and `_parse_authors()` using `FieldExtractor`.
3. **Step 3 (Abstract Reconstruction)**: Implement `_extract_abstract()` decompressing `abstract_inverted_index`.
4. **Step 4 (Normalization)**: Implement `_normalize_response()` returning typed `Document`.
5. **Step 5 (Query Translation)**: Implement `_translate_query()` mapping `Query` to `search`, `filter`, and `cursor`.
6. **Step 6 (Pagination Loop)**: Implement `search()` generator yielding documents across `cursor` updates.
7. **Step 7 (Mocked Integration Test)**: Verify pagination and filtering using `requests_mock` without live network calls.

---

## 3. Explicit Component Contract

### Class Definition: `OpenAlexProvider`
* **Query Translation (`_translate_query`)**:
  * Parameter `search`: raw query text.
  * Parameter `filter`:
    * `publication_year:{year_min}-{year_max}`
    * `language:{language}`
    * `type:article|review`
  * Parameter `per-page`: `200`.
  * Parameter `cursor`: `*` (updated to `meta.next_cursor`).
  * Parameter `mailto`: Researcher email.
* **Abstract Reassembly**:
  ```python
  def _extract_abstract(self, raw: Dict[str, Any]) -> Optional[str]:
      inverted_index = raw.get("abstract_inverted_index")
      if not inverted_index:
          return None
      word_positions = []
      for word, positions in inverted_index.items():
          for pos in positions:
              word_positions.append((pos, word))
      word_positions.sort(key=lambda x: x[0])
      return " ".join(word for _, word in word_positions)[:5000]
  ```

---

## 4. Verification & Falsifying Tests

```python
from scholar_search.providers.openalex import OpenAlexProvider
from scholar_search.core.config import ProviderConfig

def test_abstract_inverted_index_reconstruction():
    provider = OpenAlexProvider(ProviderConfig())
    raw_work = {
        "abstract_inverted_index": {
            "Deep": [0],
            "learning": [1],
            "models": [2],
            "perform": [3],
            "well.": [4]
        }
    }
    abstract = provider._extract_abstract(raw_work)
    assert abstract == "Deep learning models perform well."
```

---

## 5. AI Build Prompt

```text
Implement OpenAlexProvider in scholar_search/providers/openalex.py following Lesson 5.2.
Follow the 7-step incremental build checkpoints:
1. Static fixture loading;
2. ID and author parsing;
3. Inverted index abstract decompression;
4. Response normalization;
5. Query parameter translation;
6. Cursor pagination loop;
7. Unit tests with mocked responses in tests/test_openalex.py.
```
