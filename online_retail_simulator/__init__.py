"""Online Retail Simulator - Generate synthetic retail data for experimentation."""

from .enrich import (
    clear_enrichment_registry,
    enrich,
    list_enrichment_functions,
    register_enrichment_function,
    register_enrichment_module,
)
from .manage import JobInfo, cleanup_old_jobs, list_jobs, load_job_metadata, load_job_results
from .simulate import (
    get_simulation_function,
    list_simulation_functions,
    register_characteristics_function,
    register_metrics_function,
    register_simulation_module,
    simulate,
    simulate_characteristics,
    simulate_metrics,
)

__version__ = "0.1.0"
__all__ = [
    "simulate",
    "simulate_characteristics",
    "simulate_metrics",
    "enrich",
    "register_enrichment_function",
    "register_enrichment_module",
    "list_enrichment_functions",
    "clear_enrichment_registry",
    "register_characteristics_function",
    "register_metrics_function",
    "register_simulation_module",
    "list_simulation_functions",
    "get_simulation_function",
    "JobInfo",
    "load_job_results",
    "load_job_metadata",
    "list_jobs",
    "cleanup_old_jobs",
]
