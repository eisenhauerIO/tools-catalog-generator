"""
Example demonstrating synthesizer-based simulation using Gaussian Copula.

This script shows:
1. Loading training data from CSV
2. Training Gaussian Copula synthesizers
3. Generating synthetic product characteristics and sales metrics
"""

from online_retail_simulator import simulate_characteristics, simulate_metrics


def main():
    print("\n" + "=" * 60)
    print("SYNTHESIZER SIMULATION DEMO")
    print("=" * 60)
    print("Using Gaussian Copula synthesizer with training data\n")

    try:
        # Step 1: Generate synthetic characteristics
        print("Step 1: Generating synthetic product characteristics...")
        products_df = simulate_characteristics("simulate/config_synthesizer_simulation.yaml")

        print(f"✓ Generated {len(products_df)} synthetic products")
        print(f"✓ Columns: {list(products_df.columns)}")

        # Show category breakdown
        if 'category' in products_df.columns:
            print(f"\nCategory breakdown:")
            category_counts = products_df['category'].value_counts()
            for category, count in category_counts.items():
                print(f"  {category}: {count} products")

        # Show price statistics
        if 'price' in products_df.columns:
            print(f"\nPrice statistics:")
            print(f"  Min price: ${products_df['price'].min():.2f}")
            print(f"  Max price: ${products_df['price'].max():.2f}")
            print(f"  Mean price: ${products_df['price'].mean():.2f}")

        # Step 2: Generate synthetic metrics
        print(f"\nStep 2: Generating synthetic sales metrics...")
        sales_df = simulate_metrics(products_df, "simulate/config_synthesizer_simulation.yaml")

        print(f"✓ Generated {len(sales_df)} synthetic sales records")
        print(f"✓ Columns: {list(sales_df.columns)}")

        # Show sales statistics
        if 'revenue' in sales_df.columns:
            print(f"\nSales statistics:")
            print(f"  Total revenue: ${sales_df['revenue'].sum():.2f}")
            print(f"  Average order value: ${sales_df['revenue'].mean():.2f}")
            if 'quantity' in sales_df.columns:
                print(f"  Total quantity: {sales_df['quantity'].sum()}")

        print("\n" + "=" * 60)
        print("Complete synthesizer simulation finished!")
        print("=" * 60)
        print("This demonstrates end-to-end ML-based synthetic data generation")
        print("for both product characteristics and sales metrics.\n")

    except ImportError as e:
        print(f"❌ Error: {e}")
        print("Install SDV with: pip install online-retail-simulator[synthesizer]")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
