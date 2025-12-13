"""Single demo: simulate rule-based data and apply enrichment via config."""

from online_retail_simulator import simulate_rule_based


def main():
    # Use the enrichment demo config if available; otherwise config_basic
    config_path = "demo/config_enrichment.json"
    try:
        products_df, sales_df = simulate_rule_based(config_path)
    except FileNotFoundError:
        config_path = "demo/config_basic.json"
        products_df, sales_df = simulate_rule_based(config_path)

    print("\nDemo finished. DataFrames returned:")
    print(f"Products: {len(products_df)} rows, columns: {list(products_df.columns)}")
    print(f"Sales: {len(sales_df)} rows, columns: {list(sales_df.columns)}")


if __name__ == "__main__":
    main()
