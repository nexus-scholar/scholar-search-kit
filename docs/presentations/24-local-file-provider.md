# Episode 24: Local File Providers & Orchestration

**Objective:** Wrap the importer subsystem in the `SearchProvider` Protocol so it can be seamlessly consumed by the Deduplicator and Engine.

## 🎬 Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | We have a parser. Let's plug it into the matrix. | *Show Title Slide.* |
| 2 | **Episode Goal** | Because we built the Engine around a generic Protocol, we don't need to rewrite the Deduplicator. We just trick the Engine into thinking a file is an API. | *Highlight the goal block.* |
| 3 | **The Hybrid Pipeline** | This is the holy grail of SLR tools: pulling from Open APIs and manual database exports simultaneously, and merging them flawlessly. | *Point to the diagram.* |
| 4 | **Implementation: Query Handling** | Since the file was already queried by the researcher, we ignore the search terms. But we still apply year bounds to keep the dataset clean. | *Explain why text filtering is skipped.* |
| 5 | **Verification** | Let's run a hybrid orchestration test. | *Transition to Terminal.* |

## 💻 Terminal & Code Walkthrough

1. **Show `providers.py`**:
   - Open `src/scholar_search/providers.py`.
   - Show the new `LocalFileProvider` class.
2. **Explain the Protocol**:
   - Highlight how it implements the exact same `search()` signature as OpenAlex.
3. **The Final Run**:
   - Run the Engine taking in an `InMemoryProvider` and a `LocalFileProvider` simultaneously. Show the Deduplicator finding duplicates across the two sources!
