"""
Run all demo scripts in simulation and enrichment directories.

Discovers and executes all run_*.py files. Hard failure on any error.
"""

import glob
import subprocess
import sys


def main():
    # Find all run_*.py files in subdirectories
    demo_scripts = sorted(glob.glob("*/run_*.py"))

    if not demo_scripts:
        print("No demo scripts found")
        return

    print(f"Found {len(demo_scripts)} demo scripts")

    for script in demo_scripts:
        print(f"Running {script}...")
        subprocess.run([sys.executable, script], check=True)

    print("All demos completed successfully")


if __name__ == "__main__":
    main()
