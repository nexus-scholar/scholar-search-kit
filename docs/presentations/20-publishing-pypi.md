# Episode 20: Publishing to PyPI

**Objective:** Configure standard Python packaging metadata and demonstrate how to build and upload a wheel to PyPI.

## 🎬 Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | The code is done. Now we release it to the world. | *Show Title Slide.* |
| 2 | **Episode Goal** | We want researchers to just type `pip install scholar-search`. We have to configure the package manager to make that happen. | *Highlight the goal block.* |
| 3 | **The `pyproject.toml` Metadata** | This file tells PyPI who wrote the code, what libraries it needs, and most importantly, what terminal command to create for the user. | *Explain script entry points.* |
| 4 | **The Build Process** | PyPI doesn't take raw code. We compile it into a `Wheel` file, which is just a fancy ZIP file that installs super fast. | *Point to the diagram.* |
| 5 | **Verification** | Let's build the wheel and install it locally to prove the command works globally. | *Transition to Terminal.* |

## 💻 Terminal & Code Walkthrough

1. **Show `pyproject.toml`**:
   - Open the root `pyproject.toml`.
   - Point out the `[project.scripts]` section where we map the CLI.
2. **Build the Wheel**:
   - In the terminal, run: `python -m build`
   - Show the generated files in the `dist/` folder.
3. **Local Installation**:
   - Run: `pip install dist/scholar_search_kit-0.1.0-py3-none-any.whl`
   - Type `scholar-search --help` to prove it is now a global command.
