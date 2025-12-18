"""
Rule-based product metrics simulation (minimal skeleton).
"""

from typing import Dict

import pandas as pd


def simulate_metrics_rule_based(product_characteristics: pd.DataFrame, config: Dict) -> pd.DataFrame:
    """
    Generate synthetic daily product metrics (rule-based).
    Args:
        product_characteristics: DataFrame of product characteristics
        config: Complete configuration dictionary
    Returns:
        DataFrame of product metrics (one row per product per date, with all characteristics)
    """
    import random
    from datetime import datetime, timedelta
    from typing import Dict

    params = config["RULE"]["METRICS"]["PARAMS"]
    date_start, date_end, sale_prob, seed = (
        params["date_start"],
        params["date_end"],
        params["sale_prob"],
        params["seed"],
    )

    if seed is not None:
        random.seed(seed)

    start_date = datetime.strptime(date_start, "%Y-%m-%d")
    end_date = datetime.strptime(date_end, "%Y-%m-%d")

    rows = []
    current_date = start_date
    while current_date <= end_date:
        for _, prod in product_characteristics.iterrows():
            sale_occurred = random.random() < sale_prob
            if sale_occurred:
                quantity = random.choices([1, 2, 3, 4, 5], weights=[50, 25, 15, 7, 3])[0]
                revenue = round(prod["price"] * quantity, 2)
            else:
                quantity = 0
                revenue = 0.0
            row = prod.to_dict()
            row["date"] = current_date.strftime("%Y-%m-%d")
            row["quantity"] = quantity
            row["revenue"] = revenue
            rows.append(row)
        current_date += timedelta(days=1)
    return pd.DataFrame(rows)
