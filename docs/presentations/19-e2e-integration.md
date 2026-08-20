# Episode 19: The E2E Integration Test

**Objective:** Validate the entire system pipeline from the CLI entry point down to the file system output using Pytest fixtures.

## 🎬 Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | We've tested the puzzle pieces. Now we test the assembled box. | *Show Title Slide.* |
| 2 | **Episode Goal** | E2E tests are slow but necessary. They prove that a researcher can actually run the tool. | *Highlight the goal block.* |
| 3 | **The E2E Test Flow** | We simulate a user opening a terminal, typing a command, and then we inspect the files generated. | *Point to the diagram.* |
| 4 | **Implementation: `tmp_path`** | If tests write to your real hard drive, they are flaky. Pytest gives us a sandbox folder that gets destroyed automatically. | *Explain fixture isolation.* |
| 5 | **Implementation: Verifying JSONL** | It's not enough that the file exists; it has to be mathematically correct. We parse it and count the documents. | *Explain assertion logic.* |
| 6 | **Verification** | Let's run the final master test suite. | *Transition to Terminal.* |

## 💻 Terminal & Code Walkthrough

1. **Show `test_e2e.py`**:
   - Open `tests/test_e2e.py`.
   - Walk through how `tmp_path` is passed into the `runner.invoke` command.
2. **Show JSON parsing**:
   - Highlight the loop that counts deduplicated lines.
3. **Run the Master Test Suite**:
   - In the terminal, run: `pytest tests/`
   - Celebrate the massive wall of green checkmarks.
