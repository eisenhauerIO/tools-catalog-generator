"""
Example demonstrating default simulation using built-in rule-based generation.

This script shows:
1. Basic product catalog generation across multiple categories
2. Daily sales transaction simulation
3. Built-in rule-based approach with configurable parameters
"""

from online_retail_simulator import simulate, load_job_results


def main():
    print("\n" + "=" * 60)
    print("DEFAULT SIMULATION DEMO")
    print("=" * 60)
    print("Using built-in rule-based generation across all categories\n")

    # Generate simulation data using default rules
    print("Generating synthetic retail data...")
    job_info = simulate("config_default_simulation.yaml")
    print(f"✓ Simulation completed. Job ID: {job_info}")

    # Load results for analysis
    products_df, sales_df = load_job_results(job_info)

    print(f"✓ Generated {len(sales_df)} sales records")
    print(f"✓ Date range: {sales_df['date'].min()} to {sales_df['date'].max()}")
    print(f"✓ Products: {sales_df['asin'].nunique()} unique ASINs")
    print(f"✓ Categories: {sales_df['category'].nunique()} different categories")

    # Show category breakdown
    print(f"\nCategory breakdown:")
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

    print(f"\n✓ Results saved to: {job_info.storage_path}/{job_info.job_id}/")

    print("\n" + "=" * 60)
    print("Default simulation complete!")
    print("=" * 60)
    print("This demonstrates the built-in rule-based generation")
    print("with diverse product categories and realistic pricing.\n")


if __name__ == "__main__":
    main()
