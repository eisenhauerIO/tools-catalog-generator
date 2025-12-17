"""
Example of registering a custom rule-based simulation function.

This demonstrates how the existing rule-based simulation is just one registered
rule among potentially many others.
"""

import random
import string
from typing import Dict, Optional

import pandas as pd

from online_retail_simulator import (
    list_simulation_functions,
    register_characteristics_function,
    simulate,
)


def generate_electronics_only(config_path: str, config: Optional[Dict] = None) -> pd.DataFrame:
    """
    Custom characteristics function that generates only electronics products.

    This is an example of how to create a custom rule that follows the same
    pattern as the default rule-based simulation.
    """
    from online_retail_simulator.config_processor import process_config

    if config is None:
        config = process_config(config_path)

    rule_config = config["RULE"]
    seed = config.get("SEED", 42)
    num_products = rule_config.get("NUM_PRODUCTS", 50)

    if seed is not None:
        random.seed(seed)

    # Electronics-specific price ranges
    price_ranges = {
        "Smartphones": (200, 1200),
        "Laptops": (500, 3000),
        "Headphones": (50, 500),
        "Tablets": (150, 800),
        "Smart Watches": (100, 600),
    }

    products = []
    for i in range(num_products):
        category = random.choice(list(price_ranges.keys()))
        price_min, price_max = price_ranges[category]
        price = round(random.uniform(price_min, price_max), 2)

        # Generate ASIN
        asin = "E" + "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(9))

        products.append({
            "asin": asin,
            "category": category,
            "price": price,
        })

    return pd.DataFrame(products)


def main():
    """Demonstrate custom rule registration and usage."""
    print("=== Custom Rule Registration Demo ===\n")

    # Show available functions before registration
    print("Available functions before registration:")
    functions = list_simulation_functions()
    print(f"Characteristics: {functions['characteristics']}")
    print(f"Metrics: {functions['metrics']}\n")

    # Register our custom function
    register_characteristics_function("electronics_only", generate_electronics_only)

    # Show available functions after registration
    print("Available functions after registration:")
    functions = list_simulation_functions()
    print(f"Characteristics: {functions['characteristics']}")
    print(f"Metrics: {functions['metrics']}\n")

    # Create a config that uses our custom function
    import tempfile
    config_content = """
SEED: 42

OUTPUT:
  DIR: demo/output
  FILE_PREFIX: electronics_demo

RULE:
  CUSTOM_CHARACTERISTICS_FUNCTION: electronics_only
  NUM_PRODUCTS: 20
  DATE_START: "2024-01-01"
  DATE_END: "2024-01-07"
  SALE_PROB: 0.4
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(config_content)
        config_path = f.name

    try:
        # Run simulation with custom rule
        print("Running simulation with custom electronics-only rule...")
        df = simulate(config_path)

        print(f"Generated {len(df)} records")
        print(f"Unique categories: {df['category'].unique()}")
        print(f"Price range: ${df['price'].min():.2f} - ${df['price'].max():.2f}")
        print(f"Total revenue: ${df['revenue'].sum():.2f}")

    finally:
        import os
        os.unlink(config_path)

    print("\n=== Demo Complete ===")
    print("Key points:")
    print("- The 'default' rule is just another registered function")
    print("- Custom rules follow the same pattern as the default")
    print("- Registration happens at runtime before simulation")
    print("- Both characteristics and metrics can be customized")


if __name__ == "__main__":
    main()
