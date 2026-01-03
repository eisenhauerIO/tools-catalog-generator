"""
Enrich workflow: applies enrichment treatments to sales data.
"""

from ..manage import JobInfo, load_dataframe, save_dataframe, update_job_metadata
from .enrichment import enrich as apply_enrichment


def enrich(config_path: str, job_info: JobInfo) -> JobInfo:
    """
    Apply enrichment to sales data using a config file.

    Saves enriched results to the same job directory.

    Args:
        config_path: Path to enrichment config (YAML or JSON)
        job_info: JobInfo object to load sales data from

    Returns:
        JobInfo: Same job, now also containing enriched.csv
    """
    # Load sales from job
    sales_df = load_dataframe(job_info, "sales")
    if sales_df is None:
        raise FileNotFoundError(f"sales.csv not found in job {job_info.job_id}")

    # Apply enrichment
    enriched_df = apply_enrichment(config_path, sales_df)

    # Save enriched to same job
    save_dataframe(job_info, "enriched", enriched_df)

    # Update metadata
    update_job_metadata(job_info, is_enriched=True)

    return job_info
