"""
Development script for testing product details simulation with Claude API.
"""

from online_retail_simulator import load_dataframe, simulate_characteristics, simulate_product_details

# Step 1: Generate base products
print("1. Generating product characteristics...")
job_info = simulate_characteristics("config_product_details.yaml")
products_df = load_dataframe(job_info, "products")
print(f"   Generated {len(products_df)} products")
print(products_df)

# Step 2: Add product details via Claude
print("\n2. Adding mock product details ...")
job_info = simulate_product_details(job_info, "config_product_details.yaml")
detailed_df = load_dataframe(job_info, "products")
print(f"   Added details to {len(detailed_df)} products")
print(detailed_df)
