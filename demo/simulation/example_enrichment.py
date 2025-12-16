"""
Example script demonstrating separated simulation and enrichment workflow.

This script shows:
1. Basic retail data generation (simulation)
2. Enrichment application with treatment effects
3. Comparison of original vs enriched data
"""

from online_retail_simulator import simulate, enrich
import pandas as pd


def main():
    print("\n" + "=" * 70)
    print("SEPARATED SIMULATION + ENRICHMENT WORKFLOW")
    print("=" * 70)

    # Step 1: Generate base simulation data
    print("Step 1: Generating base simulation data...")
    sales_df = simulate("demo/config_simulation.yaml")
    print(f"✓ Generated {len(sales_df)} sales records")
    print(f"✓ Date range: {sales_df['date'].min()} to {sales_df['date'].max()}")
    print(f"✓ Products: {sales_df['asin'].nunique()} unique ASINs")

    # Step 2: Apply enrichment
    print("\nStep 2: Applying enrichment treatment...")
    enriched_df = enrich("demo/config_enrichment.yaml", sales_df)
    print(f"✓ Applied enrichment to {len(enriched_df)} sales records")
    print(f"✓ All enrichment parameters specified in config file")

    # Step 3: Compare results
    print("\nStep 3: Comparing original vs enriched data...")

    # Filter to enrichment period for comparison
    enrichment_start = "2024-11-15"
    original_post = sales_df[sales_df['date'] >= enrichment_start]
    enriched_post = enriched_df[enriched_df['date'] >= enrichment_start]

    print(f"\nPost-enrichment period ({enrichment_start} onwards):")
    print(f"Original total quantity: {original_post['quantity'].sum()}")
    print(f"Enriched total quantity: {enriched_post['quantity'].sum()}")
    print(f"Quantity lift: {((enriched_post['quantity'].sum() / original_post['quantity'].sum()) - 1) * 100:.1f}%")

    print(f"\nOriginal total revenue: ${original_post['revenue'].sum():.2f}")
    print(f"Enriched total revenue: ${enriched_post['revenue'].sum():.2f}")
    print(f"Revenue lift: {((enriched_post['revenue'].sum() / original_post['revenue'].sum()) - 1) * 100:.1f}%")

    # Show sample of enriched vs original
    print(f"\nSample comparison (first 5 records from {enrichment_start}):")
    sample_original = original_post.head(5)[['asin', 'date', 'quantity', 'revenue']]
    sample_enriched = enriched_post.head(5)[['asin', 'date', 'quantity', 'revenue']]

    print("\nOriginal:")
    print(sample_original.to_string(index=False))
    print("\nEnriched:")
    print(sample_enriched.to_string(index=False))

    print("\n" + "=" * 70)
    print("Enrichment workflow complete!")
    print("=" * 70)
    print("This demonstrates how enrichment creates treatment effects")
    print("that can be used for causal inference and A/B testing analysis.\n")


if __name__ == "__main__":
    main()
