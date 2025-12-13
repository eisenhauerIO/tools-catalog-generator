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

4. **Run the Demo Script in Hatch**
   - Run:
     ```bash
     hatch run python demo/example.py
     ```
   - If the script fails (non-zero exit code), STOP. Ask the user for input before continuing.

---

- Optionally, validate demo output or add more steps as needed.
- Reference this workflow in the README for new contributors.
