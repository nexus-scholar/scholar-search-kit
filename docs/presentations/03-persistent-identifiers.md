# Episode 3: Persistent Identifiers (`ExternalIds`)

**Objective:** Build a robust identity layer to track academic papers across multiple data sources using normalized IDs.

## 🎬 Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | Now that our project is scaffolded, we need to tackle the hardest problem in data integration: identity. | *Show Title Slide.* |
| 2 | **Episode Goal** | Different APIs return identifiers differently. To merge results later, we must standardize them right at the boundary. | *Highlight the goal block.* |
| 3 | **The Identifier Zoo** | DOIs are the worst offenders. You might get a URL, a prefixed string, or the raw ID. We funnel all of these into one true format. | *Point to the normalization flowchart.* |
| 4 | **The `ExternalIds` Dataclass** | Instead of scattering IDs across our Document model, we group them into one dedicated `ExternalIds` object. | *Explain the fields.* |
| 5 | **Implementation: Normalizing DOIs** | We use Python's `re` module to strip out any URL wrappers and `doi:` prefixes before the data ever reaches our system. | *Transition to code.* |
| 6 | **Verification** | Let's prove our regex works by running our test suite against a variety of messy DOIs. | *Transition to Terminal.* |

## 💻 Terminal & Code Walkthrough

1. **Show `models.py`**:
   - Open `src/scholar_search/models.py`.
   - Walk through the `ExternalIds` dataclass.
   - Highlight the `_normalize_doi` helper method.
2. **Show the Tests**:
   - Open `tests/test_models.py`.
   - Show the test case verifying that `https://doi.org/10.123/456` becomes `10.123/456`.
3. **Run the Tests**:
   - In the terminal, run: `pytest -k "test_external_ids"`
   - Confirm it passes.
