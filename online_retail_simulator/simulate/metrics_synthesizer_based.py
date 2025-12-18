"""
Synthesizer-based simulation backend for metrics.
Takes product_characteristics DataFrame and config path.
No error handling, hard failures only.
"""

from typing import Dict

import numpy as np
import pandas as pd


def simulate_metrics_synthesizer_based(product_characteristics: pd.DataFrame, config: Dict) -> pd.DataFrame:
    """
    Generate synthetic product metrics using Gaussian Copula synthesizer.
    Args:
        product_characteristics: DataFrame of product characteristics (unused in current implementation)
        config: Complete configuration dictionary
    Returns:
        DataFrame of synthetic metrics
    """
    try:
        from sdv.metadata import SingleTableMetadata
        from sdv.single_table import GaussianCopulaSynthesizer
    except ImportError:
        raise ImportError(
            "SDV is required for synthesizer-based simulation. "
            "Install with: pip install online-retail-simulator[synthesizer]"
        )

    params = config["SYNTHESIZER"]["METRICS"]["PARAMS"]
    training_data_path, num_rows, seed = (
        params["training_data_path"],
        params["num_rows"],
        params["seed"],
    )

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
