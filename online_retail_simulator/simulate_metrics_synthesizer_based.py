"""
Synthesizer-based simulation backend for metrics.
Takes product_characteristics DataFrame and config path.
No error handling, hard failures only.
"""

import json

import numpy as np
import pandas as pd


def simulate_metrics_synthesizer_based(product_characteristics, config_path):
    try:
        from sdv.metadata import SingleTableMetadata
        from sdv.single_table import CTGANSynthesizer, GaussianCopulaSynthesizer, TVAESynthesizer
    except ImportError:
        raise ImportError(
            "SDV is required for synthesizer-based simulation. "
            "Install with: pip install online-retail-simulator[synthesizer]"
        )

    # For demonstration, just generate random sales metrics for each product and date
    num_days = 5
    date_range = pd.date_range(start="2024-01-01", periods=num_days)
    rows = []
    for _, row in product_characteristics.iterrows():
        for date in date_range:
            quantity = np.random.poisson(5)
            price = row["price"]
            revenue = price * quantity
            rows.append(
                {
                    "asin": row["asin"],
                    "date": date,
                    "quantity": quantity,
                    "revenue": revenue,
                }
            )
    df = pd.DataFrame(rows)
    return df
