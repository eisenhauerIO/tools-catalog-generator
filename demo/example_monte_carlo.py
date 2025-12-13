"""
Example script demonstrating Monte Carlo sampling with SDV.

This script shows the full workflow:
1. Generate baseline retail data using rule-based simulator
2. Train SDV synthesizers on the simulated data
3. Generate multiple Monte Carlo samples for uncertainty quantification
"""

import json
from online_retail_simulator import simulate, train_synthesizer, generate_sample


def update_config_output_files(config_path: str, sample_num: int) -> None:
    """
    Update config file with new output filenames for Monte Carlo sample.
    
    Args:
        config_path: Path to config file
        sample_num: Sample number for output filename
    """
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    config["SDV"]["OUTPUT_PRODUCTS_FILE"] = f"mc_sample_{sample_num:03d}_products.json"
    config["SDV"]["OUTPUT_SALES_FILE"] = f"mc_sample_{sample_num:03d}_sales.json"
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)


def main():
    config_path = "demo/config_monte_carlo.json"
    
    print("\n" + "=" * 70)
    print("STEP 1: Generate Baseline Retail Data")
    print("=" * 70)
    print("Using rule-based simulator to generate synthetic products and sales.\n")
    
    products_df, sales_df = simulate(config_path)
    
    print("\n\n" + "=" * 70)
    print("STEP 2: Train SDV Synthesizers")
    print("=" * 70)
    print("Training Gaussian Copula models on products and sales data.")
    print("These models learn the statistical distributions and correlations.\n")
    
    train_synthesizer(config_path, products_df=products_df, sales_df=sales_df)
    
    print("\n\n" + "=" * 70)
    print("STEP 3: Generate Monte Carlo Samples")
    print("=" * 70)
    print("Creating 5 Monte Carlo samples for uncertainty quantification.\n")
    
    num_samples = 5
    for i in range(1, num_samples + 1):
        print(f"\n--- Generating Monte Carlo Sample {i}/{num_samples} ---")
        update_config_output_files(config_path, i)
        synthetic_products_df, synthetic_sales_df = generate_sample(config_path)
    
    print("\n" + "=" * 70)
    print("Monte Carlo Sampling Complete!")
    print("=" * 70)
    print(f"""
Generated {num_samples} Monte Carlo samples for uncertainty analysis.

Use Cases:
1. Bootstrap Analysis: Estimate confidence intervals for causal effects
2. Sensitivity Analysis: Test robustness of findings across data variations
3. Power Analysis: Assess statistical power under different scenarios
4. Model Validation: Evaluate prediction models across synthetic datasets

Output Files:
- Original data: demo/output_mc/products.json, sales.json
- Trained models: demo/output_mc/synthesizer_*.pkl
- MC samples: demo/output_mc/mc_sample_001_*.json, ..., mc_sample_005_*.json

Next Steps:
- Run analysis pipeline on each Monte Carlo sample
- Aggregate results to compute confidence intervals
- Compare treatment effects across samples for robustness
""")


if __name__ == "__main__":
    main()
