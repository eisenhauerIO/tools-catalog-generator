"""
Job management functions for simulation data.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from artifact_store import ArtifactStore


@dataclass
class JobInfo:
    """Information about a simulation job and its storage location."""

    job_id: str
    storage_path: str

    def __str__(self) -> str:
        return self.job_id

    def get_store(self) -> ArtifactStore:
        """Get an ArtifactStore for this job's directory."""
        return ArtifactStore(f"{self.storage_path}/{self.job_id}")


def generate_job_id() -> str:
    """Generate a unique job ID with timestamp and short UUID."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    short_uuid = str(uuid.uuid4())[:8]
    return f"job-{timestamp}-{short_uuid}"


def create_job(config: Dict, config_path: str, job_id: Optional[str] = None) -> JobInfo:
    """
    Create a new job directory with config.

    Args:
        config: Configuration dictionary
        config_path: Path to original config file
        job_id: Optional job ID, auto-generated if not provided

    Returns:
        JobInfo: Information about the created job
    """
    if job_id is None:
        job_id = generate_job_id()

    # Extract storage path from config
    storage_path = config.get("STORAGE", {}).get("PATH", ".")

    # Create JobInfo
    job_info = JobInfo(job_id=job_id, storage_path=storage_path)

    # Copy original config using ArtifactStore
    if Path(config_path).exists():
        store = job_info.get_store()
        source_store, filename = ArtifactStore.from_file_path(config_path)
        config_content = source_store.read_text(filename)
        store.write_text("config.yaml", config_content)

    return job_info


def save_dataframe(job_info: JobInfo, name: str, df: pd.DataFrame) -> None:
    """
    Save a DataFrame to a job directory.

    Args:
        job_info: JobInfo for the job
        name: Name of the file (without extension)
        df: DataFrame to save
    """
    store = job_info.get_store()
    store.write_csv(f"{name}.csv", df)


def load_dataframe(job_info: JobInfo, name: str) -> Optional[pd.DataFrame]:
    """
    Load a DataFrame from a job directory.

    Args:
        job_info: JobInfo for the job
        name: Name of the file (without extension)

    Returns:
        DataFrame if file exists, None otherwise
    """
    store = job_info.get_store()
    file_path = f"{name}.csv"

    if not store.exists(file_path):
        return None

    return store.read_csv(file_path)


def update_job_metadata(job_info: JobInfo, **flags) -> None:
    """
    Update job metadata with step completion flags.

    Args:
        job_info: JobInfo for the job
        **flags: Step completion flags (e.g., has_characteristics=True)
    """
    store = job_info.get_store()

    # Load existing metadata or start fresh
    if store.exists("metadata.json"):
        metadata = store.read_json("metadata.json")
    else:
        metadata = {
            "job_id": job_info.job_id,
            "storage_path": job_info.storage_path,
        }

    # Merge flags and update timestamp
    metadata.update(flags)
    metadata["timestamp"] = datetime.now().isoformat()

    store.write_json("metadata.json", metadata)


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
    job_info = create_job(config, config_path, job_id)

    save_dataframe(job_info, "products", products_df)
    save_dataframe(job_info, "sales", sales_df)
    update_job_metadata(job_info, has_characteristics=True, has_metrics=True)

    return job_info


def load_job_results(job_info: JobInfo) -> Dict[str, pd.DataFrame]:
    """
    Load simulation results for a job.

    Args:
        job_info: JobInfo containing job details

    Returns:
        Dict with available DataFrames: 'products', 'sales', 'enriched'

    Raises:
        FileNotFoundError: If job directory doesn't exist
    """
    store = job_info.get_store()

    if not store.exists(""):
        raise FileNotFoundError(f"Job directory not found: {store.base_path}")

    results = {}
    for name in ["products", "sales", "enriched"]:
        df = load_dataframe(job_info, name)
        if df is not None:
            results[name] = df

    return results


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
    store = job_info.get_store()

    if not store.exists("metadata.json"):
        raise FileNotFoundError(f"Metadata file not found: {store.full_path('metadata.json')}")

    return store.read_json("metadata.json")


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
        store = job_info.get_store()
        if store.exists(""):
            store.delete()
            removed_jobs.append(job_id)

    return removed_jobs
