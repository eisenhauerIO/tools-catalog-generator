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
        DataFrame of product characteristics
    """
    from ..config_processor import process_config

    config_loaded = process_config(config_path)

    # Simple either/or logic: RULE or SYNTHESIZER, not both, not neither
    if "RULE" in config_loaded:
        # Rule-based generation
        rule_config = config_loaded["RULE"]
        characteristics_config = rule_config["CHARACTERISTICS"]
        function_name = characteristics_config.get("FUNCTION")

        from .rule_registry import SimulationRegistry

        func = SimulationRegistry.get_characteristics_function(function_name)
        return func(config_loaded)

    elif "SYNTHESIZER" in config_loaded:
        # Synthesizer-based generation
        synthesizer_config = config_loaded["SYNTHESIZER"]
        characteristics_config = synthesizer_config["CHARACTERISTICS"]
        function_name = characteristics_config.get("FUNCTION")

        if function_name != "gaussian_copula":
            raise NotImplementedError(f"Synthesizer function '{function_name}' not implemented")

        from .characteristics_synthesizer_based import simulate_characteristics_synthesizer_based

        return simulate_characteristics_synthesizer_based(config_loaded)

    else:
        # Hard failure - no valid configuration
        raise ValueError("Config must contain either RULE or SYNTHESIZER block")
