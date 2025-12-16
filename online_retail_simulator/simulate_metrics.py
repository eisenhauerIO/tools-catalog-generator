"""
Interface for simulating product metrics.
Dispatches to rule-based implementation based on method argument.
"""

from typing import Dict, Optional

import pandas as pd


def simulate_metrics(
    product_characteristics: pd.DataFrame,
    config_path: str,
    config: Optional[Dict] = None,
) -> pd.DataFrame:
    """
    Simulate product metrics using the backend specified in config.
    Args:
        product_characteristics: DataFrame of product characteristics
        config_path: Path to JSON configuration file
        config: Optional pre-loaded config (avoids re-reading)
    Returns:
        DataFrame of product metrics
    """
    from .config_processor import process_config

    config_loaded = process_config(config_path) if config is None else config

    # Detect mode based on which block is present
    has_rule = "RULE" in config_loaded
    has_synthesizer = "SYNTHESIZER" in config_loaded

    if has_rule and not has_synthesizer:
        from .simulate_metrics_rule_based import simulate_metrics_rule_based

        return simulate_metrics_rule_based(product_characteristics, config_path)
    elif has_synthesizer and not has_rule:
        from .simulate_metrics_synthesizer_based import simulate_metrics_synthesizer_based

        return simulate_metrics_synthesizer_based(product_characteristics, config_path)
    elif has_rule and has_synthesizer:
        raise ValueError("Config must contain exactly one of RULE or SYNTHESIZER block, not both")
    else:
        raise ValueError("Config must contain either RULE or SYNTHESIZER block")
