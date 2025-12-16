"""
Synthesizer-based simulation backend.
Reads a DataFrame from the path specified in config['SYNTHESIZER']['dataframe_path'].
No error handling, hard failures only.
"""

import random
import string

import pandas as pd


def generate_random_asin(prefix: str = "B") -> str:
    """Generate a random ASIN-like identifier.
    - 10 characters total
    - Alphanumeric
    - Defaults to starting with 'B' (common for non-book ASINs)
    """
    chars = string.ascii_uppercase + string.digits
    return prefix + "".join(random.choice(chars) for _ in range(9))


def simulate_characteristics_synthesizer_based(config):
    try:
        from sdv.metadata import SingleTableMetadata
        from sdv.single_table import CTGANSynthesizer, GaussianCopulaSynthesizer, TVAESynthesizer
    except ImportError:
        raise ImportError(
            "SDV is required for synthesizer-based simulation. "
            "Install with: pip install online-retail-simulator[synthesizer]"
        )

    # For now, create dummy data since dataframe_path is not in config
    # This is a placeholder implementation
    import numpy as np

    np.random.seed(config.get("SEED", 42))
    num_rows = config["SYNTHESIZER"].get("DEFAULT_PRODUCTS_ROWS", 10)

    # Create dummy product data for demonstration
    categories = ["Electronics", "Clothing", "Books", "Home", "Sports"]
    products = []
    for i in range(num_rows):
        products.append(
            {
                "asin": generate_random_asin(),
                "category": np.random.choice(categories),
                "price": np.random.uniform(10, 1000),
            }
        )

    synthetic_df = pd.DataFrame(products)
    return synthetic_df
