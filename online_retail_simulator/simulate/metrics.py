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
    from ..config_processor import process_config

    config_loaded = process_config(config_path)

    # Simple either/or logic: RULE or SYNTHESIZER, not both, not neither
    if "RULE" in config_loaded:
        if "SYNTHESIZER" in config_loaded:
            raise ValueError("Config cannot contain both RULE and SYNTHESIZER blocks")

        # Rule-based generation
        rule_config = config_loaded["RULE"]
        if "METRICS" not in rule_config:
            raise ValueError("RULE block must contain METRICS section")

        metrics_config = rule_config["METRICS"]
        function_name = metrics_config.get("FUNCTION", "default")

        from .rule_registry import SimulationRegistry

        func = SimulationRegistry.get_metrics_function(function_name)
        return func(product_characteristics, config_loaded)

    elif "SYNTHESIZER" in config_loaded:
        # Synthesizer-based generation
        synthesizer_config = config_loaded["SYNTHESIZER"]
        metrics_config = synthesizer_config["METRICS"]
        function_name = metrics_config.get("FUNCTION")

        if function_name != "gaussian_copula":
            raise NotImplementedError(f"Metrics function '{function_name}' not implemented")

        from .metrics_synthesizer_based import simulate_metrics_synthesizer_based

        return simulate_metrics_synthesizer_based(product_characteristics, config_loaded)

    else:
        # Hard failure - no valid configuration
        raise ValueError("Config must contain either RULE or SYNTHESIZER block")
