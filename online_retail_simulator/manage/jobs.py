"""
Job management functions for simulation data.
"""

import json
import shutil
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd


@dataclass
class JobInfo:
    """Information about a simulation job and its storage location."""

    job_id: str
    storage_path: str

    def __str__(self) -> str:
        return self.job_id


def generate_job_id() -> str:
    """Generate a unique job ID with timestamp and short UUID."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    short_uuid = str(uuid.uuid4())[:8]
    return f"job-{timestamp}-{short_uuid}"


def get_job_directory(job_info: JobInfo) -> Path:
    """Get the directory path for a job."""
    return Path(job_info.storage_path) / job_info.job_id


def save_job_data(
    products_df: pd.DataFrame,
    sales_df: pd.DataFrame,
    config: Dict,
    config_path: str,
    job_id: Optional[str] = None,
) -> JobInfo:
    """
    Save simulation data with automatic job-based storage.

    Args:
        products_df: Product characteristics DataFrame
        sales_df: Sales metrics DataFrame
        config: Configuration dictionary
        config_path: Path to original config file
        job_id: Optional job ID, auto-generated if not provided

    Returns:
        JobInfo: Information about the saved job
    """
    if job_id is None:
        job_id = generate_job_id()

    # Extract storage path from config
    storage_path = config.get("STORAGE", {}).get("PATH", ".")

    # Create JobInfo
    job_info = JobInfo(job_id=job_id, storage_path=storage_path)

    # Create job directory
    job_path = get_job_directory(job_info)
    job_path.mkdir(parents=True, exist_ok=True)

    # Save data files
    products_df.to_csv(job_path / "products.csv", index=False)
    sales_df.to_csv(job_path / "sales.csv", index=False)

    # Copy original config
    if Path(config_path).exists():
        shutil.copy2(config_path, job_path / "config.yaml")

    # Create metadata
    metadata = {
        "job_id": job_id,
        "timestamp": datetime.now().isoformat(),
        "config_path": config_path,
        "storage_path": storage_path,
        "seed": config.get("SEED"),
        "mode": "RULE" if "RULE" in config else "SYNTHESIZER",
        "num_products": len(products_df),
        "num_sales": len(sales_df),
        "config": config,
    }

    # Save metadata
    with open(job_path / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2, default=str)

    return job_info


def load_job_results(job_info: JobInfo) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load simulation results for a job.

    Args:
        job_info: JobInfo containing job details

    Returns:
        Tuple of (products_df, sales_df)

    Raises:
        FileNotFoundError: If job directory or files don't exist
    """
    job_path = get_job_directory(job_info)

    if not job_path.exists():
        raise FileNotFoundError(f"Job directory not found: {job_path}")

    products_path = job_path / "products.csv"
    sales_path = job_path / "sales.csv"

    if not products_path.exists():
        raise FileNotFoundError(f"Products file not found: {products_path}")
    if not sales_path.exists():
        raise FileNotFoundError(f"Sales file not found: {sales_path}")

    products_df = pd.read_csv(products_path)
    sales_df = pd.read_csv(sales_path)

    return products_df, sales_df


def load_job_metadata(job_info: JobInfo) -> Dict:
    """
    Load metadata for a job.

    Args:
        job_info: JobInfo containing job details

    Returns:
        Dict: Job metadata

    Raises:
        FileNotFoundError: If job directory or metadata file doesn't exist
    """
    job_path = get_job_directory(job_info)
    metadata_path = job_path / "metadata.json"

    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

    with open(metadata_path, "r") as f:
        return json.load(f)


def list_jobs(storage_path: str = ".") -> List[str]:
    """
    List all available job IDs in a storage path.

    Args:
        storage_path: Base path where job directories are stored

    Returns:
        List of job IDs sorted by creation time (newest first)
    """
    output_dir = Path(storage_path)
    if not output_dir.exists():
        return []

    jobs = []
    for job_dir in output_dir.iterdir():
        if job_dir.is_dir() and job_dir.name.startswith("job-"):
            jobs.append(job_dir.name)

    # Sort by timestamp in job name (newest first)
    return sorted(jobs, reverse=True)


def cleanup_old_jobs(storage_path: str = ".", keep_count: int = 10) -> List[str]:
    """
    Clean up old job directories, keeping only the most recent ones.

    Args:
        storage_path: Base path where job directories are stored
        keep_count: Number of recent jobs to keep

    Returns:
        List of removed job IDs
    """
    jobs = list_jobs(storage_path)
    if len(jobs) <= keep_count:
        return []

    jobs_to_remove = jobs[keep_count:]
    removed_jobs = []

    for job_id in jobs_to_remove:
        job_info = JobInfo(job_id=job_id, storage_path=storage_path)
        job_path = get_job_directory(job_info)
        if job_path.exists():
            shutil.rmtree(job_path)
            removed_jobs.append(job_id)

    return removed_jobs
