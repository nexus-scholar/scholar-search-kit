# Episode 15: The Federated SearchEngine

**Objective:** Orchestrate multi-provider searches, aggregate results, and handle citation snowballing.

## Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | Bringing all 6 academic providers under a unified orchestration engine. | *Show Title Slide.* |
| 2 | **Episode Goal** | Fan out queries across OpenAlex, PubMed, Crossref, arXiv, Semantic Scholar, and bioRxiv. | *Highlight goal.* |
| 3 | **Federated Aggregation** | Collect records across sources and route them through deduplication and metadata merging. | *Show architecture diagram.* |
| 4 | **Snowballing Engine** | Direct forward citation traversal and backward reference snowballing. | *Show snowball workflow.* |
| 5 | **Implementation** | Walkthrough of `src/scholar_search/engine.py`. | *Transition to code.* |
| 6 | **Verification** | Run search engine integration tests. | *Transition to Terminal.* |

## Terminal & Code Walkthrough

1. **Show `engine.py`**:
   - Open `src/scholar_search/engine.py`.
   - Walk through `SearchEngine.search()` and `SearchEngine.snowball()`.
2. **Run the Tests**:
   - Run: `pytest tests/test_engine.py`
   - Confirm multi-provider federation passes.
