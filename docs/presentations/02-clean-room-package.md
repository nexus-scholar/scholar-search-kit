# Episode 2: Clean-Room Package Architecture

**Objective:** Scaffold a modern, maintainable Python project using `uv` and establish the `src` layout.

## 🎬 Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | Welcome back! Today we put down the foundation. No hacking scripts, we are building a production-grade tool. | *Show Title Slide.* |
| 2 | **Episode Goal** | We need a package that can be tested, installed, and distributed. We'll use `uv` for lightning-fast dependency management and strict boundaries. | *Highlight the goal block.* |
| 3 | **The Project Layout** | We use the `src` layout. This forces Python to test our installed package rather than accidentally importing local files. It prevents the "works on my machine" bug. | *Point to the flowchart.* |
| 4 | **Dependency Management with `uv`** | We are abandoning standard `pip` for `uv`. It's faster, safer, and generates rock-solid lockfiles. | *Explain why reproducibility matters.* |
| 5 | **Implementation: `pyproject.toml`** | This is the source of truth for our package. It tells Python how to install us, what our dependencies are, and where our CLI entry points live. | *Transition to code.* |
| 6 | **Verification** | If our skeleton works, `uv sync` will pass and `pytest` will report zero errors. | *Transition to Terminal.* |

## 💻 Terminal & Code Walkthrough

1. **Show `pyproject.toml`**:
   - Open the file and point out the `[project]` section.
   - Show how the CLI is registered under `[project.scripts]`.
2. **Explore the Folder Structure**:
   - Show `src/scholar_search/` vs `tests/`.
3. **Run the tooling**:
   - In the terminal, run: `uv sync`
   - Run: `pytest`
   - Show that the environment is healthy.
