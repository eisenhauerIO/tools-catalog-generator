# Full Validation Workflow

This workflow ensures the overall integrity of the repository. **If any step fails, stop immediately and ask for user input before proceeding.**

## Steps

1. **Check for Uncommitted Changes**
   - Run:
     ```bash
     git status --porcelain
     ```
   - If any files are listed (output is not empty), STOP. Ask the user how to proceed (commit, stash, or discard changes).

2. **Run the Full Test Suite**
   - Run:
     ```bash
     pytest
     ```
   - If any test fails (non-zero exit code), STOP. Ask the user for input before continuing.

3. **Run the Demo Script**
   - Run:
     ```bash
     python demo/example.py
     ```
   - If the script fails (non-zero exit code), STOP. Ask the user for input before continuing.

---

- Optionally, validate demo output or add more steps as needed.
- Reference this workflow in the README for new contributors.
