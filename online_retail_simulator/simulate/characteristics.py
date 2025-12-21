"""
Interface for simulating product characteristics.
Dispatches to rule-based or synthesizer-based implementation based on config.
"""

from ..config_processor import process_config
from ..manage import JobInfo, create_job, save_dataframe, save_job_metadata


def simulate_characteristics(config_path: str) -> JobInfo:
    """
    Simulate product characteristics using the backend specified in config.

    Args:
        config_path: Path to configuration file

    Returns:
        JobInfo: Job containing products.csv
    """
    config = process_config(config_path)

    # Generate products DataFrame
    products_df = _generate_characteristics(config)

    # Create job and save products
    job_info = create_job(config, config_path)
    save_dataframe(job_info, "products", products_df)
    save_job_metadata(job_info, config, config_path, num_products=len(products_df))

    return job_info


def _generate_characteristics(config: dict):
    """Generate characteristics DataFrame based on config backend."""

    # Simple either/or logic: RULE or SYNTHESIZER, not both, not neither
    if "RULE" in config:
        # Rule-based generation
        rule_config = config["RULE"]
        characteristics_config = rule_config["CHARACTERISTICS"]
        function_name = characteristics_config.get("FUNCTION")

        from .rule_registry import get_simulation_function

        try:
            func = get_simulation_function("characteristics", function_name)
        except KeyError as e:
            raise KeyError(f"Error in RULE.CHARACTERISTICS: {str(e)}") from e
        return func(config)

    elif "SYNTHESIZER" in config:
        # Synthesizer-based generation
        synthesizer_config = config["SYNTHESIZER"]
        characteristics_config = synthesizer_config["CHARACTERISTICS"]
        function_name = characteristics_config.get("FUNCTION")

        if function_name != "gaussian_copula":
            raise NotImplementedError(f"Synthesizer function '{function_name}' not implemented")

        from .characteristics_synthesizer_based import simulate_characteristics_synthesizer_based

        return simulate_characteristics_synthesizer_based(config)

    else:
        # Hard failure - no valid configuration
        raise ValueError("Config must contain either RULE or SYNTHESIZER block")
