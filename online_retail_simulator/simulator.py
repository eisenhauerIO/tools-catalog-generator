"""Main simulator interface for generating and exporting retail data."""

from typing import Tuple

import pandas as pd

from .simulator_rule_based import simulate_rule_based


def simulate(config_path: str, mode: str | None = None, **kwargs) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Unified simulation entrypoint driven by SIMULATOR.mode.

    Args:
        config_path: Path to JSON configuration file
        mode: Optional override; if omitted uses SIMULATOR.mode from config
        **kwargs: forwarded to synthesizer-based simulation (e.g., num_rows_products, num_rows_sales)

    Returns:
        Tuple of (products_df, sales_df) as pandas DataFrames
    """
    from .config_processor import process_config

    config = process_config(config_path)
    sim_mode = mode or config.get("SIMULATOR", {}).get("mode", "rule")

    if sim_mode == "rule":
        return simulate_rule_based(config_path, config=config)
    if sim_mode == "synthesizer":
        from .simulator_synthesizer_based import simulate_synthesizer_based
        # Expect df, num_rows, synthesizer_type in kwargs
        return simulate_synthesizer_based(**kwargs)
    raise ValueError("mode must be 'rule' or 'synthesizer'")
