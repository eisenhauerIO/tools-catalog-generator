"""
Enrich workflow: applies enrichment treatments to metrics data.
"""

from ..config_processor import process_config
from ..manage import JobInfo, save_job_metadata
from .enrichment import enrich as apply_enrichment


def enrich(config_path: str, job_info: JobInfo) -> JobInfo:
    """
    Apply enrichment to metrics data using a config file.

    Saves enriched results to the same job directory.

    Args:
        config_path: Path to enrichment config (YAML or JSON)
        job_info: JobInfo object to load metrics data from

    Returns:
        JobInfo: Same job, now also containing enriched.csv and optionally potential_outcomes.csv
    """
    # Load config
    config = process_config(config_path)

    # Load metrics from job
    metrics_df = job_info.load_df("metrics")
    if metrics_df is None:
        raise FileNotFoundError(f"metrics.csv not found in job {job_info.job_id}")

    # Load product_details (with quality_score) if available, fallback to products
    products_df = job_info.load_df("product_details")
    if products_df is None:
        products_df = job_info.load_df("products")

    # Apply enrichment (pass job_info and products for product-aware functions)
    enriched_df, potential_outcomes_df = apply_enrichment(
        config_path, metrics_df, job_info=job_info, products_df=products_df
    )

    # Save enriched to same job
    job_info.save_df("enriched", enriched_df)

    # Save potential outcomes if provided by the enrichment function
    if potential_outcomes_df is not None:
        job_info.save_df("potential_outcomes", potential_outcomes_df)

    # Update metadata
    save_job_metadata(job_info, config, config_path, is_enriched=True)

    return job_info
