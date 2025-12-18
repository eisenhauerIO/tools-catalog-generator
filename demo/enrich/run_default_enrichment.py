"""
Example demonstrating default enrichment using built-in combined_boost function.

This script shows:
1. Basic simulation data generation
2. Application of default enrichment with gradual ramp-up
3. Comparison of original vs enriched results
"""

from online_retail_simulator import simulate, enrich


def main():
    print("\n" + "=" * 60)
    print("DEFAULT ENRICHMENT DEMO")
    print("=" * 60)
    print("Using built-in 'combined_boost' function with gradual ramp-up\n")

    # Step 1: Generate base simulation data
    print("Step 1: Generating base simulation data...")
    job_id = simulate("../simulate/config_default_simulation.yaml")
    print(f"✓ Simulation completed. Job ID: {job_id}")

    # Load simulation results
    from online_retail_simulator import load_job_results

    products_df, sales_df = load_job_results(job_id)
    print(f"✓ Generated {len(sales_df)} sales records")
    print(f"✓ Date range: {sales_df['date'].min()} to {sales_df['date'].max()}")
    print(f"✓ Products: {sales_df['asin'].nunique()} unique ASINs")

    # Step 2: Apply default enrichment
    print("\nStep 2: Applying default enrichment (combined_boost)...")
    enriched_job_id = enrich("config_default_enrichment.yaml", job_id)
    print(f"✓ Enrichment completed. Job ID: {enriched_job_id}")
    print("✓ Uses gradual 7-day ramp-up with 50% max effect")

    # Load enriched results
    _, enriched_df = load_job_results(enriched_job_id)
    print(f"✓ Applied enrichment to {len(enriched_df)} sales records")

    # Step 3: Compare results
    print("\nStep 3: Comparing results...")
    enrichment_start = "2024-11-15"
    original_post = sales_df[sales_df["date"] >= enrichment_start]
    enriched_post = enriched_df[enriched_df["date"] >= enrichment_start]

    print(f"\nPost-enrichment period ({enrichment_start} onwards):")
    print(f"Original total quantity: {original_post['quantity'].sum()}")
    print(f"Enriched total quantity: {enriched_post['quantity'].sum()}")
    print(
        f"Quantity lift: {((enriched_post['quantity'].sum() / original_post['quantity'].sum()) - 1) * 100:.1f}%"
    )

    print(f"\nOriginal total revenue: ${original_post['revenue'].sum():.2f}")
    print(f"Enriched total revenue: ${enriched_post['revenue'].sum():.2f}")
    print(
        f"Revenue lift: {((enriched_post['revenue'].sum() / original_post['revenue'].sum()) - 1) * 100:.1f}%"
    )

    print(f"\n✓ Original results saved to: ./output/{job_id}/")
    print(f"✓ Enriched results saved to: ./output/{enriched_job_id}/")

    print("\n" + "=" * 60)
    print("Default enrichment complete!")
    print("=" * 60)
    print("This demonstrates the built-in combined_boost function")
    print("with gradual ramp-up for realistic A/B testing scenarios.\n")


if __name__ == "__main__":
    main()
