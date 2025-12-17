"""
Example demonstrating custom enrichment with price discount function.

This script shows:
1. Definition of a custom enrichment function
2. Registration and usage of the custom function
3. Price-based treatment effects (vs quantity-based defaults)
"""

import copy
import random
from datetime import datetime
from typing import Dict, List

from online_retail_simulator import simulate, enrich, register_enrichment_function


def price_discount(sales: List[Dict], **kwargs) -> List[Dict]:
    """
    Apply price discount to enriched products.

    Args:
        sales: List of sale transaction dictionaries
        **kwargs: Parameters including:
            - discount_percent: Percentage discount (default: 0.2 for 20% off)
            - enrichment_fraction: Fraction of products to enrich (default: 0.3)
            - enrichment_start: Start date of enrichment (default: "2024-11-15")
            - seed: Random seed for product selection (default: 42)

    Returns:
        List of modified sale dictionaries with price discount applied
    """
    discount_percent = kwargs.get("discount_percent", 0.2)
    enrichment_fraction = kwargs.get("enrichment_fraction", 0.3)
    enrichment_start = kwargs.get("enrichment_start", "2024-11-15")
    seed = kwargs.get("seed", 42)

    # Set seed for reproducibility
    if seed is not None:
        random.seed(seed)

    # Get unique products and select fraction for enrichment
    unique_products = list(set(sale["product_id"] for sale in sales))
    n_enriched = int(len(unique_products) * enrichment_fraction)
    enriched_product_ids = set(random.sample(unique_products, n_enriched))

    # Apply discount to enriched products after start date
    treated_sales = []
    start_date = datetime.strptime(enrichment_start, "%Y-%m-%d")

    for sale in sales:
        sale_copy = copy.deepcopy(sale)
        sale_date = datetime.strptime(sale_copy["date"], "%Y-%m-%d")

        # Apply discount if product is enriched and date is after start
        if sale_copy["product_id"] in enriched_product_ids and sale_date >= start_date:
            unit_price = sale_copy.get("unit_price", sale_copy.get("price"))
            discounted_price = unit_price * (1 - discount_percent)

            # Update price fields
            if "unit_price" in sale_copy:
                sale_copy["unit_price"] = round(discounted_price, 2)
            if "price" in sale_copy:
                sale_copy["price"] = round(discounted_price, 2)

            # Recalculate revenue
            sale_copy["revenue"] = round(sale_copy["quantity"] * discounted_price, 2)

        treated_sales.append(sale_copy)

    return treated_sales


def main():
    print("\n" + "=" * 60)
    print("CUSTOM ENRICHMENT DEMO")
    print("=" * 60)
    print("Using custom 'price_discount' function for promotional analysis\n")

    # Step 1: Register custom function
    print("Step 1: Registering custom enrichment function...")
    register_enrichment_function("price_discount", price_discount)
    print("✓ Registered 'price_discount' function")

    # Step 2: Generate base simulation data
    print("\nStep 2: Generating base simulation data...")
    sales_df = simulate("simulation/config_default_simulation.yaml")
    print(f"✓ Generated {len(sales_df)} sales records")
    print(f"✓ Date range: {sales_df['date'].min()} to {sales_df['date'].max()}")
    print(f"✓ Products: {sales_df['asin'].nunique()} unique ASINs")

    # Step 3: Apply custom enrichment
    print("\nStep 3: Applying custom enrichment (price_discount)...")
    enriched_df = enrich("enrichment/config_custom_enrichment.yaml", sales_df)
    print(f"✓ Applied enrichment to {len(enriched_df)} sales records")
    print("✓ Uses 25% price discount on 40% of products")

    # Step 4: Compare results
    print("\nStep 4: Comparing results...")
    enrichment_start = "2024-11-15"
    original_post = sales_df[sales_df['date'] >= enrichment_start]
    enriched_post = enriched_df[enriched_df['date'] >= enrichment_start]

    print(f"\nPost-enrichment period ({enrichment_start} onwards):")
    print(f"Original total quantity: {original_post['quantity'].sum()}")
    print(f"Enriched total quantity: {enriched_post['quantity'].sum()}")
    print(f"Quantity change: {((enriched_post['quantity'].sum() / original_post['quantity'].sum()) - 1) * 100:+.1f}%")

    print(f"\nOriginal total revenue: ${original_post['revenue'].sum():.2f}")
    print(f"Enriched total revenue: ${enriched_post['revenue'].sum():.2f}")
    print(f"Revenue change: {((enriched_post['revenue'].sum() / original_post['revenue'].sum()) - 1) * 100:+.1f}%")

    # Show average price change
    original_avg_price = (original_post['revenue'] / original_post['quantity']).mean()
    enriched_avg_price = (enriched_post['revenue'] / enriched_post['quantity']).mean()
    print(f"\nAverage unit price: ${original_avg_price:.2f} → ${enriched_avg_price:.2f}")
    print(f"Price change: {((enriched_avg_price / original_avg_price) - 1) * 100:+.1f}%")

    print("\n" + "=" * 60)
    print("Custom enrichment complete!")
    print("=" * 60)
    print("This demonstrates custom price-based treatment effects")
    print("for promotional campaigns and price elasticity analysis.\n")


if __name__ == "__main__":
    main()
