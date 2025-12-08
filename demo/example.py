"""
Example script demonstrating the online-retail-simulator package.

This script runs the simulator using a JSON configuration file.
"""

from online_retail_simulator import simulate


def main():
    # Run simulation from configuration file
    simulate("demo/config.json")


if __name__ == "__main__":
    main()
