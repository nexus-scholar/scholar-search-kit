# Episode 21: GitHub Actions & CI/CD

**Objective:** Implement a GitHub Actions workflow to run the Pytest suite and Ruff linter automatically on every pull request.

## 🎬 Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | We need a robot to guard our codebase. | *Show Title Slide.* |
| 2 | **Episode Goal** | When strangers submit code, we need proof it works before merging it. Continuous Integration is that proof. | *Highlight the goal block.* |
| 3 | **The CI Workflow** | Every `git push` triggers a fresh Ubuntu server. It installs the code, runs the tests, and reports back. | *Point to the diagram.* |
| 4 | **Implementation: Testing Multiple Versions** | Does this code work on Python 3.10? What about 3.12? GitHub Matrix tests them all simultaneously. | *Explain the Matrix strategy.* |
| 5 | **Verification** | Let's look at a live GitHub Action run. | *Transition to Terminal/Browser.* |

## 💻 Terminal & Code Walkthrough

1. **Show `ci.yml`**:
   - Open `.github/workflows/ci.yml`.
   - Walk through the `actions/checkout` and `actions/setup-python` steps.
2. **Show the Test commands**:
   - Highlight the lines where `pip install -e .[dev]` and `pytest` are invoked.
3. **The Payoff**:
   - Briefly switch to a browser (or mock it) to show a beautiful green checkmark on a Pull Request.
