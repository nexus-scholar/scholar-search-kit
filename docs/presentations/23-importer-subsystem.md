# Episode 23: The Importer Subsystem (Reading RIS)

**Objective:** Build a streaming parser that converts external database exports (RIS) back into the internal `Document` schema.

## 🎬 Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | We know how to export. Now it's time to learn how to import. | *Show Title Slide.* |
| 2 | **Episode Goal** | Not every database has an open API. If a researcher exports a file from Scopus, we need to ingest it to deduplicate it. | *Highlight the goal block.* |
| 3 | **The Pipeline Reversal** | This is the exact mirror image of our Episode 16 Exporter. We take raw text and turn it into typed Python objects. | *Point to the diagram.* |
| 4 | **Implementation: Parsing the Loop** | RIS is ancient but simple. We read line by line until we hit the "End of Record" marker, then we emit the document. | *Explain stateful parsing.* |
| 5 | **Verification** | Let's feed a raw RIS file into our importer and watch the `Document` objects come out. | *Transition to Terminal.* |

## 💻 Terminal & Code Walkthrough

1. **Show `importers.py`**:
   - Open `src/scholar_search/importers.py`.
   - Walk through the `RISImporter` and the `_build_document` method.
2. **Show the Iterator Pattern**:
   - Highlight how `yield` prevents memory bloat on massive files.
3. **Run a Quick Verification**:
   - Show a test where a raw `.ris` file with three citations is perfectly parsed.
