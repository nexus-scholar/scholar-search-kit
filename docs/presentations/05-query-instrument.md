# Episode 5: Query as a Research Instrument

**Objective:** Design a reproducible `Query` object that deterministically captures scientific search parameters.

## 🎬 Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | Now we tackle the input side of the equation: the Query. | *Show Title Slide.* |
| 2 | **Episode Goal** | In science, a search query is an instrument. If you don't calibrate and record its settings, your results are invalid. | *Highlight the goal block.* |
| 3 | **The `Query` Dataclass** | We capture the raw string, the date bounds, and language constraints in one object. | *Explain the fields.* |
| 4 | **Stable Identifiers** | How do we know if we've run this exact search before? We hash it. | *Point to the hashing diagram.* |
| 5 | **Implementation: `__post_init__`** | We use a dataclass lifecycle hook to ensure the hash is generated instantly. | *Explain `__post_init__`.* |
| 6 | **Verification** | Let's verify that two identical setups yield the exact same fingerprint. | *Transition to Terminal.* |

## 💻 Terminal & Code Walkthrough

1. **Show `models.py`**:
   - Open `src/scholar_search/models.py`.
   - Walk through the `Query` dataclass and its `__post_init__` method.
2. **Explain MD5**:
   - Mention why we use MD5 (it's fast and we aren't using it for cryptographic security, just collision-free caching).
3. **Run the Tests**:
   - In the terminal, run: `pytest -k "test_query"`
   - Show how the ID changes when `end_year` is altered.
