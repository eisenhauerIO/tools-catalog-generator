"""
Simulate workflow: combines characteristics and metrics simulation.
"""

from ..config_processor import process_config
from ..manage import JobInfo
from .characteristics import simulate_characteristics
from .metrics import simulate_metrics
from .product_details import simulate_product_details


def simulate(config_path: str) -> JobInfo:
    """
    Runs simulate_characteristics, optionally simulate_product_details, and simulate_metrics.

    All results are automatically saved to a job-based directory structure
    under the configured storage path.

    Args:
        config_path: Path to configuration file

    Returns:
        JobInfo: Information about the saved job
    """
    config = process_config(config_path)

    job_info = simulate_characteristics(config_path)

    if "PRODUCT_DETAILS" in config:
        job_info = simulate_product_details(job_info, config_path)

    job_info = simulate_metrics(job_info, config_path)
    return job_info
