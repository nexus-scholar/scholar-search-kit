# Episode 16: Pluggable Output Formats (JSONL & RIS)

**Objective:** Abstract file I/O and implement specific formatters for standard JSON streaming and academic RIS files.

## 🎬 Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | We have the data in memory. Now we need to save it to disk. | *Show Title Slide.* |
| 2 | **Episode Goal** | Different users need different formats. We can't hardcode file writing; we need a pluggable architecture. | *Highlight the goal block.* |
| 3 | **The `Exporter` Protocol** | Just like Providers, Exporters share an interface. The Engine just calls `write_chunk()` and doesn't care what format is happening underneath. | *Point to the diagram.* |
| 4 | **Implementation: JSON Lines** | JSON arrays require loading the whole file into memory to add one item. JSONL lets us append lines forever. | *Explain streaming JSON.* |
| 5 | **Implementation: RIS Format** | RIS is ancient but universal. It maps our clean `Document` model to two-letter tags like `TI` and `AU`. | *Explain RIS tags.* |
| 6 | **Verification** | Let's write our mock data to both formats and inspect the output. | *Transition to Terminal.* |

## 💻 Terminal & Code Walkthrough

1. **Show `exporters.py`**:
   - Open `src/scholar_search/export/exporters.py`.
   - Walk through the `JSONLExporter` and `RISExporter`.
2. **Show the RIS formatting logic**:
   - Highlight how authors are iterated and mapped to multiple `AU` tags.
3. **Run the Tests**:
   - In the terminal, run: `pytest tests/export/`
   - Show the assertions checking for standard RIS line endings.
