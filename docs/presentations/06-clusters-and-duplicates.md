# Episode 6: Clusters & Duplicate Aggregation

**Objective:** Design a model to safely merge duplicate papers across multiple providers without losing data provenance.

## 🎬 Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | We have documents and we have queries. Now we need to handle duplicates. | *Show Title Slide.* |
| 2 | **Episode Goal** | Deduplication is usually done by throwing away data. We won't do that. We will aggregate it. | *Highlight the goal block.* |
| 3 | **Non-Destructive Merging** | By grouping documents into a Cluster, we retain the fact that both OpenAlex and arXiv found the paper. | *Point to the diagram.* |
| 4 | **The `DocumentCluster` Model** | The cluster holds the bag of documents and computes metrics across them. | *Explain the fields.* |
| 5 | **Implementation: Confidence Metrics** | Merging isn't always exact. We need to store *how* confident we are so the researcher can audit it later. | *Discuss `match_confidence`.* |
| 6 | **Verification** | Let's test the canonical document selection logic. | *Transition to Terminal.* |

## 💻 Terminal & Code Walkthrough

1. **Show `models.py`**:
   - Open `src/scholar_search/models.py`.
   - Walk through the `DocumentCluster` dataclass.
2. **Discuss Canonical Selection**:
   - Explain how we might choose the "best" document (e.g., the one with an abstract over one without).
3. **Run the Tests**:
   - In the terminal, run: `pytest -k "test_cluster"`
   - Show how the canonical property selects the richer document.
