"""
Interface for simulating product characteristics.
Dispatches to rule-based or synthesizer-based implementation based on config.
"""

from typing import Dict, Optional

import pandas as pd


def simulate_characteristics(config_path: str, config: Optional[Dict] = None) -> pd.DataFrame:
    """
    Simulate product characteristics using the backend specified in config.
    Args:
        config_path: Path to JSON configuration file
        config: Optional pre-loaded config (avoids re-reading)
    Returns:
        List of product dictionaries
    """
    from .config_processor import process_config

    config_loaded = process_config(config_path)

    # Detect mode based on which block is present
    has_rule = "RULE" in config_loaded
    has_synthesizer = "SYNTHESIZER" in config_loaded

    if has_rule and not has_synthesizer:
        # Check if a custom rule function is specified
        rule_config = config_loaded["RULE"]
        custom_function = rule_config.get("CUSTOM_CHARACTERISTICS_FUNCTION") or rule_config.get(
            "CUSTOM_FUNCTION", "default"
        )

        from .rule_registry import SimulationRegistry

        func = SimulationRegistry.get_characteristics_function(custom_function)
        return func(config_path, config_loaded)

    elif has_synthesizer and not has_rule:
        from .simulate_characteristics_synthesizer_based import simulate_characteristics_synthesizer_based

        return simulate_characteristics_synthesizer_based(config_loaded)
    elif has_rule and has_synthesizer:
        raise ValueError("Config must contain exactly one of RULE or SYNTHESIZER block, not both")
    else:
        raise ValueError("Config must contain either RULE or SYNTHESIZER block")
