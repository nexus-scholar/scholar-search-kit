# Episode 20: Packaging & Publishing (`pyproject.toml`)

**Objective:** Package `scholar-search-kit` as a professional, standard Python wheel with clean entry points.

## Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | From source code to installable package. | *Show Title Slide.* |
| 2 | **Episode Goal** | Build and validate a distributable wheel with `uv build` and `scholar-search` CLI scripts. | *Highlight goal.* |
| 3 | **`pyproject.toml`** | Modern PEP 621 metadata, dependencies (`requests`, `requests-cache`, `pydantic`, `typer`), and CLI entry points. | *Show pyproject.toml snippet.* |
| 4 | **Build & Test** | Packaging the package using `uv build` and testing isolated installation. | *Show build output.* |
| 5 | **Publishing** | Safe publishing to PyPI with trusted publishing tokens. | *Explain deployment.* |
| 6 | **Verification** | Verify wheel creation. | *Transition to Terminal.* |

## Terminal & Code Walkthrough

1. **Show `pyproject.toml`**:
   - Walk through dependencies and `[project.scripts]`.
2. **Build the Wheel**:
   - Run: `uv build`
