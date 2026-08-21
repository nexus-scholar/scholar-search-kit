# Episode 10: Query Lexing & Translation

**Objective:** Tokenize complex search expressions with quotes, fields, and operators into provider query syntax.

## Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | Translating human search intent into database-specific query languages. | *Show Title Slide.* |
| 2 | **Episode Goal** | Support quoted phrases, Boolean operators (`AND`, `OR`, `NOT`), and field specifiers (`title:`, `author:`). | *Highlight goal.* |
| 3 | **The `QueryParser`** | Lexes raw input strings into structured `QueryToken` streams. | *Show parser flowchart.* |
| 4 | **Dialect Translation** | Maps tokens to S2 bulk syntax (`+`, `|`, `-`), OpenAlex filters, or arXiv prefix codes. | *Explain translator mapping.* |
| 5 | **Implementation** | Walkthrough of `src/scholar_search/query_translator.py`. | *Transition to code.* |
| 6 | **Verification** | Run our tokenization and translation unit tests. | *Transition to Terminal.* |

## Terminal & Code Walkthrough

1. **Show `query_translator.py`**:
   - Open `src/scholar_search/query_translator.py`.
   - Walk through `QueryToken`, `QueryParser`, and `BooleanQueryTranslator`.
2. **Run the Tests**:
   - Run: `pytest tests/test_query_translator.py`
   - Confirm all tests pass.
