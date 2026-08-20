# Episode 15: The Orchestrator Engine

**Objective:** Build the central `SearchEngine` class that manages the lifecycle of a query across providers, rate limiters, and deduplicators.

## 🎬 Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | We have all the puzzle pieces. Now we assemble the box. | *Show Title Slide.* |
| 2 | **Episode Goal** | The Orchestrator coordinates the pipeline. It doesn't fetch data, it doesn't dedup data, it just tells the other classes when to do their jobs. | *Highlight the goal block.* |
| 3 | **The Orchestration Flow** | Request data $\rightarrow$ Check Cache $\rightarrow$ Deduplicate $\rightarrow$ Stream to Exporter. | *Point to the diagram.* |
| 4 | **Implementation: Dependency Injection** | If the Engine hardcoded `OpenAlexProvider()`, we couldn't test it. By passing dependencies in, testing is trivial. | *Explain DI principles.* |
| 5 | **Implementation: The Run Loop** | We use Python generators (`yield`) so that if the user aborts halfway through, we still have the data we processed so far. | *Explain streaming vs batching.* |
| 6 | **Verification** | Let's stitch the mocks together and watch the engine roar to life. | *Transition to Terminal.* |

## 💻 Terminal & Code Walkthrough

1. **Show `engine.py`**:
   - Open `src/scholar_search/engine.py`.
   - Walk through the `__init__` constructor and Dependency Injection.
2. **Show the `execute` generator**:
   - Highlight the `for chunk in provider.search(...)` loop.
3. **Run the Tests**:
   - In the terminal, run: `pytest tests/test_engine.py`
   - Show how the mock provider data successfully passes through the deduplicator.
