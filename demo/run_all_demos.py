"""
Run all demo scripts in simulation and enrichment directories.

Discovers and executes all run_*.py files. Hard failure on any error.
"""

import glob
import subprocess
import sys


def main():
    import os

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Find all run_*.py files in subdirectories
    demo_scripts = []
    for root, dirs, files in os.walk(script_dir):
        for file in files:
            if (
                file.startswith("run_")
                and file.endswith(".py")
                and file != "run_all_demos.py"
            ):
                # Store both the directory and the script name
                script_path = os.path.join(root, file)
                demo_scripts.append((root, file, script_path))

    # Sort by script path for consistent ordering
    demo_scripts = sorted(demo_scripts, key=lambda x: x[2])

    if not demo_scripts:
        print("No demo scripts found")
        return

    print(f"Found {len(demo_scripts)} demo scripts")

    for script_dir, script_name, script_path in demo_scripts:
        print(f"\nRunning {os.path.relpath(script_path)}...")
        try:
            # Execute the script in its own directory
            subprocess.run([sys.executable, script_name], check=True, cwd=script_dir)
            print(f"✓ {os.path.relpath(script_path)} completed successfully")
        except subprocess.CalledProcessError as e:
            print(
                f"✗ {os.path.relpath(script_path)} failed with exit code {e.returncode}"
            )
            raise

    print("\n" + "=" * 60)
    print("All demos completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
