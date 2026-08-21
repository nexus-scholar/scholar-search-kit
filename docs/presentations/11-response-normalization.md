# Episode 11: Response Normalization Subsystem

**Objective:** Clean, parse, and standardize diverse academic payloads into uniform `Document` models.

## Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | Transforming messy JSON and XML payloads into immaculate research records. | *Show Title Slide.* |
| 2 | **Episode Goal** | Parse authors, dates, HTML-stripped abstracts, and identifiers without falsifying evidence. | *Highlight goal.* |
| 3 | **Author Parsing** | Unpacks strings like `"Alan M. Turing"` into `given_name` and `family_name`. | *Show parsing examples.* |
| 4 | **Date Normalization** | Converts ISO dates, Crossref `date-parts`, and XML dates into standard 4-digit years. | *Show date formats.* |
| 5 | **Abstract Cleansing** | Inverted-index abstract reconstruction and XML tag stripping. | *Show before/after.* |
| 6 | **Verification** | Run our author and normalization unit tests. | *Transition to Terminal.* |

## Terminal & Code Walkthrough

1. **Demonstrate Name & Date Parsing**:
   - Walk through author splitting and date parsing utilities across providers.
2. **Run Tests**:
   - Run: `pytest tests/test_models.py -k "test_author"`
