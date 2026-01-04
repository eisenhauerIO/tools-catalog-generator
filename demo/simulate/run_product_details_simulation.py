"""
Example demonstrating product details simulation using Claude API.

This script shows:
1. Generating base product characteristics
2. Enriching products with Claude-generated titles, descriptions, brands
3. Graceful skip when ANTHROPIC_API_KEY is not set
"""

import os

from online_retail_simulator import load_job_results, simulate_characteristics, simulate_product_details

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config_product_details_simulation.yaml")


def main():
    print("\n" + "=" * 60)
    print("PRODUCT DETAILS SIMULATION DEMO")
    print("=" * 60)
    print("Generate product titles, descriptions, brands using Claude API\n")

    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("⚠ ANTHROPIC_API_KEY not set - skipping demo")
        print("  Set the environment variable to run this demo")
        return

    # Step 1: Generate base products
    print("1. Generating base product characteristics...")
    job_info = simulate_characteristics(CONFIG_PATH)
    products_df = load_job_results(job_info)["products"]
    print(f"   ✓ Generated {len(products_df)} products")

    # Step 2: Add product details via Claude
    print("\n2. Enriching with Claude-generated details...")
    job_info = simulate_product_details(job_info, CONFIG_PATH)
    detailed_df = load_job_results(job_info)["products"]
    print(f"   ✓ Added details to {len(detailed_df)} products")

    # Step 3: Display results
    print("\n3. Sample product details:")
    print("-" * 60)
    for _, row in detailed_df.head(3).iterrows():
        print(f"   ASIN: {row['asin']}")
        print(f"   Title: {row.get('title', 'N/A')}")
        print(f"   Brand: {row.get('brand', 'N/A')}")
        desc = row.get("description", "N/A")
        if desc and len(desc) > 80:
            desc = desc[:80] + "..."
        print(f"   Description: {desc}")
        print()

    print("=" * 60)
    print("✓ Product details simulation complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
