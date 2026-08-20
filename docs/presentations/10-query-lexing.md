# Episode 10: Query Lexing & Translation

**Objective:** Abstract upstream provider query syntaxes by implementing a unified Boolean query parser and translator subsystem.

## 🎬 Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | We are now building the brains of our querying engine: Lexing. | *Show Title Slide.* |
| 2 | **Episode Goal** | If you force a researcher to write 5 different query strings for 5 different APIs, the tool is useless. We need one string to rule them all. | *Highlight the goal block.* |
| 3 | **The Parsing Pipeline** | The pipeline is three steps: take raw text, break it into logical tokens, and then ask the Provider to translate those tokens. | *Point to the lexing diagram.* |
| 4 | **Implementation: `QueryLexer`** | The Lexer scans the string and classifies chunks. Quotes are respected, boolean operators are separated. | *Explain `QueryToken` types.* |
| 5 | **Implementation: Translators** | A Translator just loops over the Tokens and applies rules. "Dumb" APIs just get keywords. Smart APIs get full boolean trees. | *Explain Translator strategies.* |
| 6 | **Verification** | Let's feed a complex string into our Lexer and see what it spits out. | *Transition to Terminal.* |

## 💻 Terminal & Code Walkthrough

1. **Show `lexer.py`**:
   - Open `src/scholar_search/query/lexer.py`.
   - Walk through the token emission logic and state tracking (inside vs outside quotes).
2. **Show `translators.py`**:
   - Demonstrate the `BooleanQueryTranslator`.
3. **Run the Tests**:
   - In the terminal, run: `pytest -k "test_lexer"`
   - Show how parenthesis and operators are properly segregated.
