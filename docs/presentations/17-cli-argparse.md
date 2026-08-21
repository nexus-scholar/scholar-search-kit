# Episode 17: Command Line Interface (Typer)

**Objective:** Build a modern, user-facing Typer CLI with Rich formatting, progress spinners, and subcommands.

## Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | Building a beautiful, developer-friendly terminal interface. | *Show Title Slide.* |
| 2 | **Episode Goal** | Provide interactive and batch subcommands (`search`, `snowball`, `import`, `dedup`, `export`). | *Highlight goal.* |
| 3 | **Typer & Rich** | Using Typer with Rich tables, status spinners, and syntax highlighting. | *Show CLI screenshot.* |
| 4 | **Command Architecture** | Decoupled subcommands calling core engine, deduplicator, and verifier. | *Explain architecture.* |
| 5 | **Implementation** | Walkthrough of `src/scholar_search/cli.py`. | *Transition to code.* |
| 6 | **Verification** | Run live CLI commands in the terminal. | *Transition to Terminal.* |

## Terminal & Code Walkthrough

1. **Show `cli.py`**:
   - Open `src/scholar_search/cli.py`.
   - Walk through the `@app.command()` definitions.
2. **Run the CLI**:
   - Run: `scholar-search --help`
   - Run: `scholar-search search "attention is all you need" --limit 2`
   - Show the Rich results table.
