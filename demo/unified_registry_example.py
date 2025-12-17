"""
Example demonstrating the unified registry approach for both simulation rules and enrichment functions.

This shows how both the existing rule-based simulation and enrichment functions
are treated as registered functions, with defaults automatically available.
"""

import tempfile
from typing import Dict, List, Optional

import pandas as pd

from online_retail_simulator import (
    enrich,
    list_enrichment_functions,
    list_simulation_functions,
    register_characteristics_function,
    register_enrichment_function,
    simulate,
)


def generate_books_only(config_path: str, config: Optional[Dict] = None) -> pd.DataFrame:
    """Custom rule that generates only book products."""
    import random
    import string

    from online_retail_simulator.config_processor import process_config

    if config is None:
        config = process_config(config_path)

    rule_config = config["RULE"]
    seed = config.get("SEED", 42)
    num_products = rule_config.get("NUM_PRODUCTS", 50)

    if seed is not None:
        random.seed(seed)

    # Book-specific categories and pricing
    book_categories = {
        "Fiction": (8, 25),
        "Non-Fiction": (12, 40),
        "Textbooks": (50, 300),
        "Children's Books": (5, 20),
        "Technical Books": (30, 150),
    }

    products = []
    for i in range(num_products):
        category = random.choice(list(book_categories.keys()))
        price_min, price_max = book_categories[category]
        price = round(random.uniform(price_min, price_max), 2)

        # Generate book-style ASIN
        asin = "B" + "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(9))

        products.append({
            "asin": asin,
            "category": category,
            "price": price,
        })

    return pd.DataFrame(products)


def price_reduction(sales: List[Dict], **kwargs) -> List[Dict]:
    """Custom enrichment that reduces prices instead of boosting quantity."""
    import copy
    import random
    from datetime import datetime

    price_reduction_percent = kwargs.get("price_reduction_percent", 0.15)  # 15% price reduction
    enrichment_fraction = kwargs.get("enrichment_fraction", 0.3)
    enrichment_start = kwargs.get("enrichment_start", "2024-11-15")
    seed = kwargs.get("seed", 42)

    if seed is not None:
        random.seed(seed)

    # Get unique products and select fraction for enrichment
    unique_products = list(set(sale["product_id"] for sale in sales))
    n_enriched = int(len(unique_products) * enrichment_fraction)
    enriched_product_ids = set(random.sample(unique_products, n_enriched))

    # Apply price reduction to enriched products after start date
    treated_sales = []
    start_date = datetime.strptime(enrichment_start, "%Y-%m-%d")

    for sale in sales:
        sale_copy = copy.deepcopy(sale)
        sale_date = datetime.strptime(sale_copy["date"], "%Y-%m-%d")

        # Apply price reduction if product is enriched and date is after start
        if sale_copy["product_id"] in enriched_product_ids and sale_date >= start_date:
            unit_price = sale_copy.get("unit_price", sale_copy.get("price"))
            reduced_price = unit_price * (1 - price_reduction_percent)

            # Update price fields
            if "unit_price" in sale_copy:
                sale_copy["unit_price"] = round(reduced_price, 2)
            if "price" in sale_copy:
                sale_copy["price"] = round(reduced_price, 2)

            # Recalculate revenue
            sale_copy["revenue"] = round(sale_copy["quantity"] * reduced_price, 2)

        treated_sales.append(sale_copy)

    return treated_sales


def main():
    """Demonstrate unified registry approach."""
    print("=== Unified Registry System Demo ===\n")

    # Show default functions are automatically available
    print("1. Default functions automatically registered:")
    sim_functions = list_simulation_functions()
    enrich_functions = list_enrichment_functions()
    print(f"   Simulation functions: {sim_functions}")
    print(f"   Enrichment functions: {enrich_functions}\n")

    # Register custom functions
    print("2. Registering custom functions...")
    register_characteristics_function("books_only", generate_books_only)
    register_enrichment_function("price_reduction", price_reduction)

    # Show updated function lists
    sim_functions = list_simulation_functions()
    enrich_functions = list_enrichment_functions()
    print(f"   Updated simulation functions: {sim_functions}")
    print(f"   Updated enrichment functions: {enrich_functions}\n")

    # Test custom simulation rule
    print("3. Testing custom books-only simulation rule...")

    books_config = """
SEED: 42

OUTPUT:
  DIR: demo/output
  FILE_PREFIX: books_demo

RULE:
  CUSTOM_CHARACTERISTICS_FUNCTION: books_only
  NUM_PRODUCTS: 25
  DATE_START: "2024-01-01"
  DATE_END: "2024-01-07"
  SALE_PROB: 0.4
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(books_config)
        books_config_path = f.name

    try:
        books_df = simulate(books_config_path)
        print(f"   Generated {len(books_df)} book sales records")
        print(f"   Categories: {books_df['category'].unique()}")
        print(f"   Price range: ${books_df['price'].min():.2f} - ${books_df['price'].max():.2f}\n")
    finally:
        import os
        os.unlink(books_config_path)

    # Test custom enrichment function
    print("4. Testing custom price reduction enrichment...")

    enrichment_config = """
IMPACT:
  FUNCTION: price_reduction
  PARAMS:
    price_reduction_percent: 0.20
    enrichment_fraction: 0.4
    enrichment_start: "2024-01-02"
    seed: 123
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(enrichment_config)
        enrichment_config_path = f.name

    try:
        enriched_df = enrich(enrichment_config_path, books_df)

        original_revenue = books_df["revenue"].sum()
        enriched_revenue = enriched_df["revenue"].sum()

        print(f"   Original total revenue: ${original_revenue:.2f}")
        print(f"   Enriched total revenue: ${enriched_revenue:.2f}")
        print(f"   Revenue change: {((enriched_revenue - original_revenue) / original_revenue * 100):+.1f}%\n")
    finally:
        import os
        os.unlink(enrichment_config_path)

    # Test using default functions
    print("5. Testing default functions still work...")

    default_sim_config = """
SEED: 456

OUTPUT:
  DIR: demo/output
  FILE_PREFIX: default_demo

RULE:
  NUM_PRODUCTS: 15
  DATE_START: "2024-01-01"
  DATE_END: "2024-01-05"
  SALE_PROB: 0.3
"""

    default_enrich_config = """
IMPACT:
  FUNCTION: combined_boost
  PARAMS:
    effect_size: 0.4
    ramp_days: 3
    enrichment_fraction: 0.5
    enrichment_start: "2024-01-02"
    seed: 789
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f1, \
         tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f2:

        f1.write(default_sim_config)
        f2.write(default_enrich_config)
        default_sim_path = f1.name
        default_enrich_path = f2.name

    try:
        # Use default simulation rule
        default_df = simulate(default_sim_path)
        print(f"   Default simulation generated {len(default_df)} records")

        # Use default enrichment function
        default_enriched_df = enrich(default_enrich_path, default_df)

        original_qty = default_df["quantity"].sum()
        enriched_qty = default_enriched_df["quantity"].sum()

        print(f"   Default enrichment: {original_qty} → {enriched_qty} quantity")
        print(f"   Boost factor: {enriched_qty / original_qty:.2f}x\n")

    finally:
        import os
        os.unlink(default_sim_path)
        os.unlink(default_enrich_path)

    print("=== Demo Complete ===")
    print("Key insights:")
    print("- Default functions are automatically registered and available")
    print("- Custom functions follow the same patterns as defaults")
    print("- Both simulation rules and enrichment functions use unified registry approach")
    print("- Existing configs work unchanged (they use the registered defaults)")
    print("- All functions are treated equally - no special cases")


if __name__ == "__main__":
    main()
