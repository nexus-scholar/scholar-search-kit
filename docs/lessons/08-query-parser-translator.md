# Lesson 4.1: Query Lexing & Translation (`query_translator.py`)

## 1. Scientific Motivation & Context
Researchers construct complex Boolean literature searches with quoted phrases, field specifiers, and operators (e.g. `title:"systematic review" AND (deep OR neural)`). Every database implements different syntax dialects:
* arXiv uses field codes like `ti:`, `abs:`, `all:`.
* Semantic Scholar uses bulk operators (`+`, `|`, `-`).
* OpenAlex uses `search=` with filter strings.
* Crossref uses `query.bibliographic` and `query.title`.

Our query subsystem tokenizes generic search strings into structured tokens and translates them deterministically to target provider syntax without losing scientific constraints.

---

## 2. Component Contract & Implementation

* **Module**: `scholar_search.query_translator`
* **Components**: `QueryToken`, `QueryField`, `QueryParser`, `BooleanQueryTranslator`

```python
from enum import Enum
from dataclasses import dataclass


class QueryField(Enum):
    ALL = "all"
    TITLE = "title"
    ABSTRACT = "abstract"
    AUTHOR = "author"
    VENUE = "venue"
    YEAR = "year"


@dataclass
class QueryToken:
    value: str
    field: QueryField = QueryField.ALL
    is_phrase: bool = False
    is_operator: bool = False
```

---

## 3. Tokenizer Invariants

1. **Quoted Phrases**: Preserves multi-word strings within quotes as a single token with `is_phrase=True`.
2. **Boolean Operators**: Normalizes `AND`, `OR`, `NOT` as operator tokens.
3. **Field Prefixing**: Syntaxes like `title:"deep learning"` or `author:bengio` tag the token with the appropriate `QueryField`.
4. **Parentheses**: Captures nesting parentheses for Boolean precedence.

---

## 4. Verification & Automated Tests

Run with `pytest tests/test_query_translator.py`:

```python
from scholar_search.query_translator import (
    QueryParser,
    QueryField,
    BooleanQueryTranslator,
)


def test_query_parser_tokens():
    parser = QueryParser()
    tokens = parser.parse('title:"deep learning" AND (robotics OR vision)')

    assert tokens[0].field == QueryField.TITLE
    assert tokens[0].value == "deep learning"
    assert tokens[0].is_phrase is True
    assert tokens[1].value == "AND"
    assert tokens[1].is_operator is True


def test_boolean_translator():
    translator = BooleanQueryTranslator()
    parser = QueryParser()
    tokens = parser.parse("machine learning AND robotics")
    s2_query = translator.translate_to_s2(tokens)
    assert s2_query == "machine learning + robotics"
```
