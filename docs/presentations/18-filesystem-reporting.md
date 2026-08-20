# Episode 18: File System Export & Reporting

**Objective:** Build a robust, cross-platform file writer that isolates execution runs into timestamped directories containing both data and metadata.

## 🎬 Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | We have a CLI, but right now it just dumps files in the root folder. Let's fix that. | *Show Title Slide.* |
| 2 | **Episode Goal** | If you do 10 searches, you will overwrite your files. We need isolated, timestamped workspaces for every run. | *Highlight the goal block.* |
| 3 | **The Output Architecture** | Every run generates a folder. Inside is the data, the logs, and the metadata receipt. | *Point to the directory tree diagram.* |
| 4 | **Implementation: `RunReport`** | True reproducibility means we need a JSON file stating exactly what parameters created this data payload. | *Explain metadata logging.* |
| 5 | **Safe Path Generation** | Never concatenate strings to make file paths. `pathlib` protects us from Windows/Linux slash differences and sanitizes file names. | *Explain `pathlib` benefits.* |
| 6 | **Verification** | Let's trigger a run and inspect the newly created filesystem artifacts. | *Transition to Terminal.* |

## 💻 Terminal & Code Walkthrough

1. **Show `reporting.py`**:
   - Open `src/scholar_search/export/reporting.py`.
   - Walk through the `RunMetadata` dataclass and `Path` generation logic.
2. **Run a Live CLI Command**:
   - In the terminal, run: `python -m scholar_search "Quantum Computing" --provider in_memory`
3. **Inspect the Output**:
   - Open the newly generated `outputs/` directory.
   - Show the timestamped folder and open the `run_metadata.json` file to prove reproducibility.
