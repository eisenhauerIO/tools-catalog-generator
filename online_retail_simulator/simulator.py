"""Main simulator interface for generating and exporting retail data."""

from typing import Tuple

import pandas as pd

from .simulator_rule_based import simulate_rule_based


def simulate(config_path: str, mode: str = "rule_based", **kwargs) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Unified simulation entrypoint.
    
    Args:
        config_path: Path to JSON configuration file
        mode: "rule_based" or "synthesizer_based"
        **kwargs: forwarded to synthesizer-based simulation (e.g., num_rows_products, num_rows_sales)
    
    Returns:
        Tuple of (products_df, sales_df) as pandas DataFrames
    """
    if mode == "rule_based":
        return simulate_rule_based(config_path)
    elif mode == "synthesizer_based":
        # Lazy import to avoid SDV dependency when not used
        from .simulator_synthesizer_based import simulate_synthesizer_based
        return simulate_synthesizer_based(config_path, **kwargs)
    else:
        raise ValueError("mode must be 'rule_based' or 'synthesizer_based'")
