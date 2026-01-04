# Full Validation Workflow

This workflow ensures the overall integrity of the repository. **If any step fails, stop immediately and ask for user input before proceeding.**

All steps must be run inside a freshly pruned [hatch](https://hatch.pypa.io/) environment to ensure a clean and reproducible state.

## Steps

1. **Prune the Hatch Environment**
   - Run:
     ```bash
     hatch env prune
     ```
   - This removes all existing environments and ensures a clean start.


2. **Check for Uncommitted or Untracked Files**
   - Run:
     ```bash
     git status --porcelain
     ```
   - If any files are listed (output is not empty), STOP. This means there are either uncommitted changes or files not under version control (untracked files).
   - Ask the user how to proceed (commit, stash, discard changes, or add untracked files to version control).

3. **Run the Full Test Suite in Hatch**
   - Run:
     ```bash
     hatch run pytest
     ```
   - If any test fails (non-zero exit code), STOP. Ask the user for input before continuing.

4. **Run Pre-commit Hooks**
   - Run:
     ```bash
     pre-commit run --all-files
     ```
   - This validates code formatting (black), import sorting (isort), linting (flake8), and other hooks.
   - If any hook fails (non-zero exit code), STOP. Ask the user for input before continuing.

5. **Run All Demo Scripts in Hatch**
   - Run:
     ```bash
     cd demo && hatch run python run_all_demos.py
     ```
   - If any demo script fails (non-zero exit code), STOP. Ask the user for input before continuing.

6. **Verify Documentation Integrity**
   - Build the Sphinx documentation:
     ```bash
     cd docs && hatch run docs
     ```
   - If the build fails or produces warnings, STOP. Ask the user for input before continuing.
   - Manually verify (spot check):
     * No duplicate user stories across README.md and docs/user-guide.md
     * No duplicate configuration examples across docs/
     * Data schemas only appear in docs/user-guide.md (other files should link)
     * All internal cross-references point to correct locations
     * Code examples match actual API (check against `online_retail_simulator/__init__.py`)
   - See [maintain-documentation.md](maintain-documentation.md) for the complete content ownership matrix

---
