# Episode 11: Response Normalization Subsystem

**Objective:** Build a defensive toolkit for extracting nested data and parsing chaotic API responses into the `Document` contract.

## 🎬 Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | It's time to build the machinery that enforces our Document contract. | *Show Title Slide.* |
| 2 | **Episode Goal** | Extracting data from third-party JSON is dangerous. If we do it carelessly, we get `KeyError`s. We need safe extraction tools. | *Highlight the goal block.* |
| 3 | **The Normalization Philosophy** | We use defensive programming. We build isolated parsers for dates, authors, and IDs that never crash. | *Explain `FieldExtractor`.* |
| 4 | **Implementation: `ResponseNormalizer` Protocol** | By defining a `Protocol`, we force every future API integration to provide a parser that yields our `Document`. | *Point to the diagram.* |
| 5 | **Verification** | Let's test the date parser against some truly awful date strings. | *Transition to Terminal.* |

## 💻 Terminal & Code Walkthrough

1. **Show `normalization.py`**:
   - Open `src/scholar_search/utils/normalization.py`.
   - Show how `FieldExtractor` uses `dict.get()` recursively.
2. **Show `DateParser`**:
   - Explain how it handles partial ISO strings (e.g., just "2019" vs "2019-10-01").
3. **Run the Tests**:
   - In the terminal, run: `pytest -k "test_normalization"`
   - Prove that garbage data results in safe `None` values instead of runtime crashes.
