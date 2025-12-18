"""
Synthesizer-based simulation backend.
Reads a DataFrame from the path specified in config['SYNTHESIZER']['dataframe_path'].
No error handling, hard failures only.
"""

import random
import string
from typing import Dict

import pandas as pd


def generate_random_asin(prefix: str = "B") -> str:
    """Generate a random ASIN-like identifier.
    - 10 characters total
    - Alphanumeric
    - Defaults to starting with 'B' (common for non-book ASINs)
    """
    chars = string.ascii_uppercase + string.digits
    return prefix + "".join(random.choice(chars) for _ in range(9))


def simulate_characteristics_synthesizer_based(config: Dict) -> pd.DataFrame:
    """
    Generate synthetic product characteristics using Gaussian Copula synthesizer.
    Args:
        config: Complete configuration dictionary
    Returns:
        DataFrame of synthetic characteristics
    """
    try:
        from sdv.metadata import SingleTableMetadata
        from sdv.single_table import GaussianCopulaSynthesizer
    except ImportError:
        raise ImportError(
            "SDV is required for synthesizer-based simulation. "
            "Install with: pip install online-retail-simulator[synthesizer]"
        )

    params = config["SYNTHESIZER"]["CHARACTERISTICS"]["PARAMS"]
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
    import numpy as np

    np.random.seed(seed)
    synthetic_data = synthesizer.sample(num_rows=num_rows)

    return synthetic_data
