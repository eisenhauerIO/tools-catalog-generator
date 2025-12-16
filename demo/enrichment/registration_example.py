"""Example demonstrating enrichment function registration and usage."""

import os
import tempfile
from pathlib import Path

from online_retail_simulator import (
    enrich,
    list_enrichment_functions,
    register_enrichment_function,
    register_enrichment_module,
    simulate,
)


def simple_boost(sales, **kwargs):
    """Simple quantity boost function for demonstration."""
    boost = kwargs.get("boost", 1.2)

    for sale in sales:
        sale["quantity"] = int(sale["quantity"] * boost)
        unit_price = sale.get("unit_price", sale.get("price"))
        sale["revenue"] = round(sale["quantity"] * unit_price, 2)

    return sales


def main():
    """Demonstrate enrichment function registration."""
    print("=== Enrichment Function Registration Demo ===\n")

    # Generate some test data first
    config_path = Path(__file__).parent.parent / "config_rule.yaml"
    print(f"Generating test data using: {config_path}")
    sales_df = simulate(str(config_path))
    print(f"Generated {len(sales_df)} sales records\n")

    # 1. Direct function registration
    print("1. Registering a simple function directly...")
    register_enrichment_function("simple_boost", simple_boost)
    print(f"Registered functions: {list_enrichment_functions()}\n")

    # 2. Module registration
    print("2. Registering functions from custom_effects module...")
    # Import the module first to make it available
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    register_enrichment_module("custom_effects")
    print(f"All registered functions: {list_enrichment_functions()}\n")

    # 3. Use registered function in enrichment
    print("3. Using registered function 'simple_boost'...")

    # Create temporary config for simple_boost
    config_content = """
IMPACT:
  FUNCTION: "simple_boost"
  PARAMS:
    boost: 1.5
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(config_content)
        temp_config = f.name

    try:
        # Apply enrichment using registered function
        enriched_df = enrich(temp_config, sales_df)

        original_total = sales_df["quantity"].sum()
        enriched_total = enriched_df["quantity"].sum()

        print(f"Original total quantity: {original_total}")
        print(f"Enriched total quantity: {enriched_total}")
        print(f"Boost factor: {enriched_total / original_total:.2f}\n")

    finally:
        os.unlink(temp_config)

    # 4. Use custom module function
    print("4. Using custom module function 'price_discount'...")

    config_content = """
IMPACT:
  FUNCTION: "price_discount"
  PARAMS:
    discount_percent: 0.15
    enrichment_fraction: 0.5
    enrichment_start: "2024-01-02"
    seed: 123
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(config_content)
        temp_config = f.name

    try:
        # Apply price discount enrichment
        discounted_df = enrich(temp_config, sales_df)

        original_revenue = sales_df["revenue"].sum()
        discounted_revenue = discounted_df["revenue"].sum()

        print(f"Original total revenue: ${original_revenue:.2f}")
        print(f"Discounted total revenue: ${discounted_revenue:.2f}")
        print(f"Revenue change: {((discounted_revenue - original_revenue) / original_revenue * 100):+.1f}%\n")

    finally:
        os.unlink(temp_config)

    # 5. Use category boost function
    print("5. Using custom module function 'category_boost'...")

    config_content = """
IMPACT:
  FUNCTION: "category_boost"
  PARAMS:
    target_categories: ["Electronics", "Books"]
    boost_factor: 2.0
    enrichment_start: "2024-01-02"
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(config_content)
        temp_config = f.name

    try:
        # Apply category boost
        boosted_df = enrich(temp_config, sales_df)

        # Compare Electronics category specifically
        electronics_original = sales_df[sales_df["category"] == "Electronics"]["quantity"].sum()
        electronics_boosted = boosted_df[boosted_df["category"] == "Electronics"]["quantity"].sum()

        print(f"Electronics original quantity: {electronics_original}")
        print(f"Electronics boosted quantity: {electronics_boosted}")
        if electronics_original > 0:
            print(f"Electronics boost factor: {electronics_boosted / electronics_original:.2f}")

    finally:
        os.unlink(temp_config)

    print("\n=== Demo Complete ===")
    print("Key takeaways:")
    print("- Functions can be registered directly or from modules")
    print("- Registered functions work seamlessly with existing config system")
    print("- Multiple custom effects can be registered and used")
    print("- Registration happens at runtime before calling enrich()")


if __name__ == "__main__":
    main()
