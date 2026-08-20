# Episode 4: The Normalized Document & Author Model

**Objective:** Define the central schemas that all provider responses will map into, enforcing strict boundaries and data integrity.

## 🎬 Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | Now we define the absolute core of our system: the Document. | *Show Title Slide.* |
| 2 | **Episode Goal** | If we let messy provider JSON leak into our business logic, we're doomed. We need a strict wall. | *Highlight the goal block.* |
| 3 | **The Normalization Boundary** | Every API has a different opinion on how to format a paper. We force them all into our shape. | *Point to the diagram.* |
| 4 | **The `Document` Model** | By leveraging Python dataclasses, we get type hints and strict structures for free. | *Explain the key fields.* |
| 5 | **Implementation: UTC Timestamps** | Auditability is a strict requirement for scientific tools. We must log exactly *when* we saw a record. | *Explain the `retrieved_at` field.* |
| 6 | **Verification** | Let's look at the actual code and run our instantiation tests. | *Transition to Terminal.* |

## 💻 Terminal & Code Walkthrough

1. **Show `models.py`**:
   - Open `src/scholar_search/models.py`.
   - Walk through the `Author` and `Document` dataclasses.
2. **Show Provenance Fields**:
   - Highlight `provider_id` and `retrieved_at`. Explain why these matter for reproducible research.
3. **Run the Tests**:
   - In the terminal, run: `pytest tests/test_models.py`
   - Show how Python rejects invalid instantiations if required fields are missing.
