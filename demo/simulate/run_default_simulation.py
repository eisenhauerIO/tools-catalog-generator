"""
Example demonstrating default simulation using built-in rule-based generation.

This script shows:
1. Basic product catalog generation across multiple categories
2. Daily and weekly sales transaction simulation
3. Built-in rule-based approach with configurable parameters
4. Customer journey funnel metrics (impressions → visits → cart adds → orders)
"""

from online_retail_simulator import simulate, load_job_results
import pandas as pd
import yaml


def analyze_results(sales_df, products_df, granularity, job_info):
    """Display analysis for the given granularity.

    Args:
        sales_df: Sales DataFrame with metrics
        products_df: Products DataFrame
        granularity: "daily" or "weekly"
        job_info: Job information object
    """
    print(f"✓ Generated {len(sales_df)} sales records")
    print(f"✓ Date range: {sales_df['date'].min()} to {sales_df['date'].max()}")
    print(f"✓ Products: {sales_df['asin'].nunique()} unique ASINs")
    print(f"✓ Categories: {sales_df['category'].nunique()} different categories")

    # Granularity-specific info
    if granularity == "weekly":
        dates_dt = pd.to_datetime(sales_df["date"])
        all_mondays = all(dates_dt.dt.weekday == 0)
        print(f"✓ All dates are Mondays (ISO week start): {all_mondays}")
        print(f"✓ Number of weeks: {sales_df['date'].nunique()}")
    else:
        print(f"✓ Number of days: {sales_df['date'].nunique()}")

    # Show category breakdown
    print(f"\nCategory breakdown:")
    category_counts = sales_df["category"].value_counts()
    for category, count in category_counts.items():
        print(f"  {category}: {count} sales")

    # Show funnel metrics and revenue summary
    print(f"\nFunnel metrics:")
    print(f"  Total impressions: {sales_df['impressions'].sum():,}")
    print(f"  Total visits: {sales_df['visits'].sum():,}")
    print(f"  Total cart adds: {sales_df['cart_adds'].sum():,}")
    print(f"  Total ordered units: {sales_df['ordered_units'].sum():,}")

    # Calculate conversion rates
    if sales_df['impressions'].sum() > 0:
        conversion_rate = sales_df['ordered_units'].sum() / sales_df['impressions'].sum()
        print(f"  Overall conversion rate: {conversion_rate:.2%}")

    print(f"\nRevenue summary:")
    print(
        f"  Price range: ${sales_df['price'].min():.2f} - ${sales_df['price'].max():.2f}"
    )
    print(f"  Total revenue: ${sales_df['revenue'].sum():,.2f}")
    print(f"  Average order value: ${sales_df['revenue'].mean():.2f}")

    print(f"\n✓ Results saved to: {job_info.storage_path}/{job_info.job_id}/")


def main():
    granularities = ["daily", "weekly"]

    for granularity in granularities:
        print("\n" + "=" * 60)
        print(f"DEFAULT SIMULATION DEMO - {granularity.upper()} GRANULARITY")
        print("=" * 60)
        print(f"Using built-in rule-based generation with {granularity} aggregation\n")

        # Load base config
        config = yaml.safe_load(open("config_default_simulation.yaml"))

        # Set granularity
        config["RULE"]["METRICS"]["PARAMS"]["granularity"] = granularity

        # Update storage path to separate daily and weekly outputs
        config["STORAGE"]["PATH"] = f"output/sim_demo_{granularity}"

        # Save temporary config
        temp_config_path = f"/tmp/config_demo_{granularity}.yaml"
        with open(temp_config_path, "w") as f:
            yaml.dump(config, f)

        # Generate simulation data
        print(f"Generating synthetic retail data ({granularity})...")
        job_info = simulate(temp_config_path)
        print(f"✓ Simulation completed. Job ID: {job_info}")

        # Load results for analysis
        products_df, sales_df = load_job_results(job_info)

        # Display analysis
        analyze_results(sales_df, products_df, granularity, job_info)

    print("\n" + "=" * 60)
    print("Default simulation complete!")
    print("=" * 60)
    print("This demonstrates the built-in rule-based generation")
    print("with diverse product categories and realistic funnel metrics.")
    print("\nBoth daily and weekly granularities have been generated,")
    print("allowing you to choose the appropriate level of detail")
    print("for your analysis.\n")


if __name__ == "__main__":
    main()
