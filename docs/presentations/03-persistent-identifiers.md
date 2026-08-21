# Episode 3: Persistent Identifiers (`ExternalIds`)

**Objective:** Build a robust identity layer to track academic papers across multiple data sources using normalized IDs.

## Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | Now that our project is scaffolded, we tackle the core foundation of data integration: identity. | *Show Title Slide.* |
| 2 | **Episode Goal** | Different APIs return identifiers differently. To merge results accurately, we standardize them at the boundary. | *Highlight goal.* |
| 3 | **The Identifier Zoo** | DOIs can arrive as URLs, prefixed strings, or raw text. We funnel them into one lowercase, prefix-free format. | *Show normalization diagram.* |
| 4 | **The `ExternalIds` Dataclass** | We group DOIs, arXiv IDs, PMIDs, OpenAlex IDs, and S2 IDs into one typed `ExternalIds` object. | *Explain fields.* |
| 5 | **Implementation: `__post_init__`** | Dataclass `__post_init__` cleanses whitespace, strips HTTP/DOI prefixes, and converts empty strings to `None`. | *Transition to code.* |
| 6 | **Verification** | We run automated tests verifying messy DOIs and arXiv prefixes. | *Transition to Terminal.* |

## Terminal & Code Walkthrough

1. **Show `models.py`**:
   - Open `src/scholar_search/models.py`.
   - Walk through the `ExternalIds` dataclass and its `__post_init__` prefix-stripping logic.
2. **Show the Tests**:
   - Open `tests/test_models.py`.
   - Walk through `test_external_ids_normalization`.
3. **Run the Tests**:
   - Run: `pytest tests/test_models.py -k "test_external_ids"`
   - Confirm tests pass.
