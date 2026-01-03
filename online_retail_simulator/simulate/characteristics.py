"""
Interface for simulating product characteristics.
Dispatches to appropriate backend based on config.
"""

from ..config_processor import process_config
from ..core.backends import BackendRegistry
from ..manage import JobInfo, create_job, save_dataframe, update_job_metadata


def simulate_characteristics(config_path: str) -> JobInfo:
    """
    Simulate product characteristics using the backend specified in config.

    Args:
        config_path: Path to configuration file

    Returns:
        JobInfo: Job containing products.csv
    """
    config = process_config(config_path)

    # Generate products DataFrame via backend
    backend = BackendRegistry.detect_backend(config)
    products_df = backend.simulate_characteristics()

    # Create job and save products
    job_info = create_job(config, config_path)
    save_dataframe(job_info, "products", products_df)
    update_job_metadata(job_info, has_characteristics=True)

    return job_info
