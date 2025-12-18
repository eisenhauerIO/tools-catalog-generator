"""
Synthesizer-based simulation backend for metrics.
Takes product_characteristics DataFrame and config path.
No error handling, hard failures only.
"""

import json

import numpy as np
import pandas as pd


def simulate_metrics_synthesizer_based(product_characteristics, config_path, config=None):
    try:
        from sdv.metadata import SingleTableMetadata
        from sdv.single_table import GaussianCopulaSynthesizer
    except ImportError:
        raise ImportError(
            "SDV is required for synthesizer-based simulation. "
            "Install with: pip install online-retail-simulator[synthesizer]"
        )

    from ..config_processor import process_config

    config_loaded = process_config(config_path) if config is None else config
    synthesizer_config = config_loaded["SYNTHESIZER"]

    # Get METRICS config - REQUIRED
    if "METRICS" not in synthesizer_config:
        raise ValueError("SYNTHESIZER block must contain METRICS section")

    metrics_config = synthesizer_config["METRICS"]

    # Get function (synthesizer type)
    function_name = metrics_config.get("FUNCTION")
    if not function_name:
        raise ValueError("FUNCTION is required in METRICS section")
    if function_name != "gaussian_copula":
        raise NotImplementedError(
            f"Metrics function '{function_name}' not implemented. " "Only 'gaussian_copula' is supported."
        )

    # Get parameters
    if "PARAMS" not in metrics_config:
        raise ValueError("PARAMS is required in METRICS section")
    params = metrics_config["PARAMS"]

    # Get required parameters
    training_data_path = params.get("training_data_path")
    if not training_data_path:
        raise ValueError("training_data_path is required in PARAMS")

    num_rows = params.get("num_rows")
    if not num_rows:
        raise ValueError("num_rows is required in PARAMS")

    seed = params.get("seed")
    if seed is None:
        raise ValueError("seed is required in PARAMS")

    # Load training data
    training_data = pd.read_csv(training_data_path)

    # Step 1: Create metadata and synthesizer
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(training_data)
    synthesizer = GaussianCopulaSynthesizer(metadata)

    # Step 2: Train the synthesizer
    synthesizer.fit(training_data)

    # Step 3: Generate synthetic data with seed
    np.random.seed(seed)
    synthetic_metrics = synthesizer.sample(num_rows=num_rows)

    return synthetic_metrics
