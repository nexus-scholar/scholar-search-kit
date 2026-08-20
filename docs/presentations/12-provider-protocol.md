# Episode 12: The Provider Protocol & In-Memory Engine

**Objective:** Define the structural typing interface for Search Providers and implement an in-memory mock for local offline testing.

## 🎬 Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | It's time to build the actual Search Engine. But we start with a fake one. | *Show Title Slide.* |
| 2 | **Episode Goal** | If our tests require Wi-Fi, they are bad tests. We need an abstraction layer so our business logic doesn't care where the data comes from. | *Highlight the goal block.* |
| 3 | **The `SearchProvider` Protocol** | By using a Python Protocol, we get strong static typing without forcing inheritance. If it walks like a provider, it is a provider. | *Point to the diagram.* |
| 4 | **Implementation: `InMemoryProvider`** | We load it with a hardcoded list of `Document` objects. This allows us to test deduplication and export later. | *Explain the mock data concept.* |
| 5 | **The Registry Pattern** | The CLI needs a way to look up providers by string names. The Registry handles this mapping. | *Explain dependency injection via Registry.* |
| 6 | **Verification** | Let's prove we can swap out the backend seamlessly. | *Transition to Terminal.* |

## 💻 Terminal & Code Walkthrough

1. **Show `base.py`**:
   - Open `src/scholar_search/providers/base.py`.
   - Walk through the `SearchProvider` Protocol and `BaseProvider` abstract class.
2. **Show `in_memory.py`**:
   - Walk through the `InMemoryProvider`.
3. **Run the Tests**:
   - In the terminal, run: `pytest -k "test_in_memory_provider"`
   - Show how fast and reliably it returns the mock data.
