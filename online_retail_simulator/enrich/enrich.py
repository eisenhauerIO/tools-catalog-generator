"""
Enrich workflow: applies enrichment treatments to sales data.
"""

from typing import Optional

import pandas as pd

from .enrichment import enrich as apply_enrichment


def enrich(config_path: str, job_id: str) -> str:
    """
    Apply enrichment to sales data using a config file.

    All results are automatically saved to a job-based directory structure
    under ./output/job-<timestamp>-<uuid>/

    Args:
        config_path: Path to enrichment config (YAML or JSON)
        job_id: Job ID to load sales data from

    Returns:
        str: New job ID for accessing the stored enriched results
    """
    from ..config_processor import process_config
    from ..manage import load_job_results, save_job_data

    # Load data from job
    products_df, sales_df = load_job_results(job_id)

    # Apply enrichment
    enriched_df = apply_enrichment(config_path, sales_df)

    # Load config for metadata
    config = process_config(config_path)

    # Save enriched results to new job
    new_job_id = save_job_data(sales_df, enriched_df, config, config_path)

    return new_job_id
