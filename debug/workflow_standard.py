import json
from pathlib import Path
from online_retail_simulator.simulator import simulate
from online_retail_simulator.simulator_synthesizer_based import simulate_synthesizer_based

# Path to your config file (adjust as needed)
config_path = str(Path(__file__).parent.parent / "demo" / "config_synthesizer.json")

# Step 1: Run rule-based simulation to get products and sales DataFrames
products_df, sales_df = simulate(config_path, mode="rule")
print(f"Rule-based simulation: {len(products_df)} products, {len(sales_df)} sales")

# Step 2: Merge DataFrames for synthesizer input
merged_df = sales_df.merge(products_df, on="product_id", how="left")
print(f"Merged DataFrame: {merged_df.shape}")

# Step 3: Generate synthetic data from merged DataFrame
synthetic_df = simulate_synthesizer_based(merged_df, num_rows=len(merged_df))
print(f"Synthetic DataFrame: {synthetic_df.shape}")

# Optionally, save synthetic data to a file
output_path = Path(__file__).parent / "synthetic_merged.json"
synthetic_df.to_json(output_path, orient="records", indent=2)
print(f"Synthetic data saved to {output_path}")
