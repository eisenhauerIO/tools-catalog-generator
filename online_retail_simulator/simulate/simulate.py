"""
Simulate workflow: combines characteristics and metrics simulation.
"""

from .characteristics import simulate_characteristics
from .metrics import simulate_metrics


def simulate(config_path):
    """
    Runs simulate_characteristics and simulate_metrics in sequence.

    All results are automatically saved to a job-based directory structure
    under the configured storage path.

    Args:
        config_path: Path to configuration file

    Returns:
        JobInfo: Information about the saved job
    """
    from ..config_processor import process_config
    from ..manage import save_job_data

    config = process_config(config_path)

    # Generate data
    products = simulate_characteristics(config_path)
    sales = simulate_metrics(products, config_path)

    # Save with automatic job-based storage
    job_info = save_job_data(products, sales, config, config_path)

    return job_info
