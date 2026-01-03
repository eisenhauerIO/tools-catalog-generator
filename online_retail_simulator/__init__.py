"""Online Retail Simulator - Generate synthetic retail data for experimentation."""

from .enrich import (
    clear_enrichment_registry,
    enrich,
    list_enrichment_functions,
    register_enrichment_function,
    register_enrichment_module,
)
from .manage import (
    JobInfo,
    cleanup_old_jobs,
    create_job,
    list_jobs,
    load_dataframe,
    load_job_metadata,
    load_job_results,
    save_dataframe,
)
from .simulate import (
    get_simulation_function,
    list_simulation_functions,
    register_characteristics_function,
    register_metrics_function,
    register_simulation_module,
    simulate,
    simulate_characteristics,
    simulate_metrics,
    simulate_product_details,
)

__version__ = "0.1.0"
__all__ = [
    # Simulation
    "simulate",
    "simulate_characteristics",
    "simulate_product_details",
    "simulate_metrics",
    # Enrichment
    "enrich",
    "register_enrichment_function",
    "register_enrichment_module",
    "list_enrichment_functions",
    "clear_enrichment_registry",
    # Custom simulation registration
    "register_characteristics_function",
    "register_metrics_function",
    "register_simulation_module",
    "list_simulation_functions",
    "get_simulation_function",
    # Job management
    "JobInfo",
    "create_job",
    "save_dataframe",
    "load_dataframe",
    "load_job_results",
    "load_job_metadata",
    "list_jobs",
    "cleanup_old_jobs",
]
