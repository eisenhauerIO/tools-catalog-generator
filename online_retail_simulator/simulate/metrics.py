"""
Interface for simulating product metrics.
Dispatches to appropriate backend based on config.
"""

from ..config_processor import process_config
from ..core.backends import BackendRegistry
from ..manage import JobInfo, load_dataframe, save_dataframe, save_job_metadata


def simulate_metrics(job_info: JobInfo, config_path: str) -> JobInfo:
    """
    Simulate product metrics using the backend specified in config.

    Args:
        job_info: JobInfo containing products.csv
        config_path: Path to configuration file

    Returns:
        JobInfo: Same job, now also containing sales.csv
    """
    config = process_config(config_path)

    # Load products from job
    products_df = load_dataframe(job_info, "products")
    if products_df is None:
        raise FileNotFoundError(f"products.csv not found in job {job_info.job_id}")

    # Generate sales DataFrame via backend
    backend = BackendRegistry.detect_backend(config)
    sales_df = backend.simulate_metrics(products_df)

    # Save sales to same job
    save_dataframe(job_info, "sales", sales_df)
    save_job_metadata(
        job_info,
        config,
        config_path,
        num_products=len(products_df),
        num_sales=len(sales_df),
    )

    return job_info
