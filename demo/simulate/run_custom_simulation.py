"""
Example demonstrating custom simulation with electronics-only generation.

This script shows:
1. Definition of a custom characteristics function
2. Registration and usage of the custom function
3. Specialized product generation (electronics-only vs all categories)
"""

import random
import string
from typing import Dict, Optional

import pandas as pd
from online_retail_simulator import simulate, register_characteristics_function


def generate_electronics_only(
    config_path: str, config: Optional[Dict] = None
) -> pd.DataFrame:
    """
    Custom characteristics function that generates only electronics products.

    This demonstrates how to create a custom rule that follows the same
    pattern as the default rule-based simulation but with specialized logic.
    """
    from online_retail_simulator.config_processor import process_config

    if config is None:
        config = process_config(config_path)

    rule_config = config["RULE"]
    seed = config.get("SEED", 42)
    num_products = rule_config.get("NUM_PRODUCTS", 50)

    if seed is not None:
        random.seed(seed)

    # Electronics-specific categories and price ranges
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

        # Generate electronics-style ASIN
        asin = "E" + "".join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(9)
        )

        products.append(
            {
                "asin": asin,
                "category": category,
                "price": price,
            }
        )

    return pd.DataFrame(products)


def main():
    print("\n" + "=" * 60)
    print("CUSTOM SIMULATION DEMO")
    print("=" * 60)
    print("Using custom 'electronics_only' generation function\n")

    # Step 1: Register custom function
    print("Step 1: Registering custom simulation function...")
    register_characteristics_function("electronics_only", generate_electronics_only)
    print("✓ Registered 'electronics_only' function")

    # Step 2: Generate simulation data using custom rule
    print("\nStep 2: Generating synthetic retail data...")
    job_id = simulate("config_custom_simulation.yaml")
    print(f"✓ Simulation completed. Job ID: {job_id}")

    # Load results for analysis
    from online_retail_simulator import load_job_results

    products_df, sales_df = load_job_results(job_id)

    print(f"✓ Generated {len(sales_df)} sales records")
    print(f"✓ Date range: {sales_df['date'].min()} to {sales_df['date'].max()}")
    print(f"✓ Products: {sales_df['asin'].nunique()} unique ASINs")
    print(f"✓ Categories: {sales_df['category'].nunique()} electronics categories only")

    # Show category breakdown (should be electronics only)
    print(f"\nElectronics category breakdown:")
    category_counts = sales_df["category"].value_counts()
    for category, count in category_counts.items():
        print(f"  {category}: {count} sales")

    # Show price and revenue summary
    print(f"\nSummary statistics:")
    print(
        f"  Price range: ${sales_df['price'].min():.2f} - ${sales_df['price'].max():.2f}"
    )
    print(f"  Total quantity: {sales_df['quantity'].sum()}")
    print(f"  Total revenue: ${sales_df['revenue'].sum():.2f}")
    print(f"  Average order value: ${sales_df['revenue'].mean():.2f}")

    print(f"\n✓ Results saved to: ./output/{job_id}/")

    print("\n" + "=" * 60)
    print("Custom simulation complete!")
    print("=" * 60)
    print("This demonstrates custom product generation logic")
    print("with specialized categories and pricing rules.\n")


if __name__ == "__main__":
    main()
