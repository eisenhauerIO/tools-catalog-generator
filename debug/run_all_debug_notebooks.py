#!/usr/bin/env python3
"""
Executes all Jupyter notebooks in the debug directory using nbconvert.
Terminates immediately if any notebook fails.
"""
import subprocess
import sys
from pathlib import Path

NOTEBOOK_DIR = Path(__file__).parent
notebooks = sorted(NOTEBOOK_DIR.glob("*.ipynb"))

if not notebooks:
    print("No notebooks found in debug directory.")
    sys.exit(0)

for nb in notebooks:
    output_name = f"executed_{nb.name}"
    print(f"Running {nb.name} ...")
    try:
        subprocess.run([
            sys.executable, "-m", "jupyter", "nbconvert",
            "--to", "notebook",
            "--execute", str(nb),
            "--output", output_name
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Execution failed for {nb.name}.")
        sys.exit(1)
    print(f"Finished {nb.name}")
