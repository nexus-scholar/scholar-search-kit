# Lesson 4.1: Query Lexing & Translation (`query_translator.py`)

## 1. Scientific Motivation & Context
Researchers construct complex Boolean literature searches using parentheses, quotes, field specifiers, and operators (e.g. `title:"systematic review" AND (deep OR neural) NOT author:Smith`). Every database API implements different syntax rules:
* arXiv uses field codes like `ti:`, `abs:`, `all:`.
* Semantic Scholar bulk uses `+` (AND), `|` (OR), `-` (NOT).
* OpenAlex uses `search=` for terms and comma-delimited `filter=` strings.
* Crossref uses `query=` and `filter=`.
A robust query subsystem must parse generic expressions into an Abstract Syntax Tree / token stream and translate them accurately to provider dialects without dropping scientific constraints silently.

## 2. Reference Architecture Analysis
* **Reference Source**: `strategy-pipeline/src/slr/providers/query_translator.py`
* **Components**:
  * `QueryToken`: Holds `value`, `field: QueryField`, `is_phrase: bool`, `is_operator: bool`.
  * `QueryParser`: Tokenizes strings into terms, phrases, fields (`title:`, `author:`, `year:`), operators (`AND`, `OR`, `NOT`), and parentheses.
  * Translators: `BaseQueryTranslator`, `SimpleQueryTranslator`, `BooleanQueryTranslator`, `StructuredQueryTranslator`.

## 3. Explicit Component Contract

### 3.1 `QueryParser`
* **Tokenization Rules**:
  1. Parentheses: `(` and `)` are extracted as individual operator tokens.
  2. Field prefix: `(\w+):` sets the active `QueryField` for the immediate next token.
  3. Quoted phrase: `"([^"]*)"` extracts exact inner phrase (`is_phrase=True`).
  4. Boolean operators: `AND`, `OR`, `NOT` (case-insensitive).
  5. Terms: Non-whitespace words.
* **Validation (`validate`)**: Checks for balanced parentheses. Returns `False` if unbalanced.

### 3.2 Translators
* **`SimpleQueryTranslator`**: Returns `{"q": query.text, **filter_params}`.
* **`BooleanQueryTranslator`**: Maps tokens to provider field codes and operator mappings.
* **`StructuredQueryTranslator`**: Emits nested dictionary queries with `$and`, `$or`, `$not`.

## 4. Verification & Falsifying Tests

```python
from scholar_search.providers.query_translator import QueryParser, QueryField

def test_query_parser_tokens():
    parser = QueryParser()
    tokens = parser.parse('title:"deep learning" AND (robotics OR vision)')
    
    assert tokens[0].field == QueryField.TITLE
    assert tokens[0].value == "deep learning"
    assert tokens[0].is_phrase is True
    
    assert tokens[1].value == "AND"
    assert tokens[1].is_operator is True
    
    assert tokens[2].value == "("
    assert tokens[3].value == "robotics"
    assert tokens[4].value == "OR"
    assert tokens[5].value == "vision"
    assert tokens[6].value == ")"
    
    assert parser.validate(tokens) is True

def test_unbalanced_parentheses():
    parser = QueryParser()
    tokens = parser.parse('deep learning AND (robotics')
    assert parser.validate(tokens) is False
```

## 5. AI Build Prompt

```text
Implement QueryParser, QueryToken, QueryField, and Translators in scholar_search/providers/query_translator.py following Lesson 4.1.
Support phrase matching, field specifiers (title:, author:), operators (AND, OR, NOT), parentheses, and balanced syntax validation.
Add unit tests in tests/test_query_translator.py.
```
