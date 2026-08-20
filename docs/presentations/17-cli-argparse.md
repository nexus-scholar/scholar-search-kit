# Episode 17: Command Line Interface (Argparse)

**Objective:** Build a user-facing CLI that parses arguments, handles configuration injection, and gracefully reports errors.

## 🎬 Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | The engine is built. It's time to build the steering wheel. | *Show Title Slide.* |
| 2 | **Episode Goal** | Our tool is only as good as its interface. We need a terminal command that researchers can run out-of-the-box. | *Highlight the goal block.* |
| 3 | **CLI Architecture** | The CLI is the translation layer. It takes string arguments, grabs the right Python classes from our Registries, and boots the engine. | *Point to the diagram.* |
| 4 | **Implementation: `argparse`** | Python's built-in `argparse` handles all the boilerplate for help menus and input validation. | *Explain the defined arguments.* |
| 5 | **Handling Secrets** | A quick security note: API keys in CLI arguments end up in your bash history. We use Environment Variables instead. | *Explain `os.environ` usage.* |
| 6 | **Verification** | Let's ask our tool for help, and then run a real in-memory query from the command line. | *Transition to Terminal.* |

## 💻 Terminal & Code Walkthrough

1. **Show `cli.py`**:
   - Open `src/scholar_search/cli.py`.
   - Walk through the `argparse` setup and the `main()` function entry point.
2. **Show the Help Menu**:
   - In the terminal, run: `python -m scholar_search --help`
   - Show the auto-generated documentation.
3. **Run an In-Memory Query**:
   - Run: `python -m scholar_search "AI" --provider in_memory --format jsonl`
   - Show the output printing correctly.
