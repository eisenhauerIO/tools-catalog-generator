"""
Rule-based product characteristics simulation.
"""

import random
import string
from typing import Dict, List, Optional

import pandas as pd


def generate_random_asin(prefix: str = "B") -> str:
    """Generate a random ASIN-like identifier.
    - 10 characters total
    - Alphanumeric
    - Defaults to starting with 'B' (common for non-book ASINs)
    """
    chars = string.ascii_uppercase + string.digits
    return prefix + "".join(random.choice(chars) for _ in range(9))


# ...existing code...
_CATEGORIES = [
    "Electronics",
    "Clothing",
    "Home & Garden",
    "Books",
    "Sports & Outdoors",
    "Toys & Games",
    "Food & Beverage",
    "Health & Beauty",
]

_PRICE_RANGES = {
    "Electronics": (50, 1500),
    "Clothing": (15, 200),
    "Home & Garden": (20, 500),
    "Books": (10, 60),
    "Sports & Outdoors": (15, 300),
    "Toys & Games": (10, 100),
    "Food & Beverage": (5, 50),
    "Health & Beauty": (8, 80),
}


def simulate_characteristics_rule_based(config_path: str, config: Optional[Dict] = None) -> pd.DataFrame:
    """
    Generate synthetic product characteristics (rule-based).
    Args:
        config_path: Path to JSON configuration file
        config: Optional pre-loaded config (avoids re-reading)
    Returns:
        DataFrame of product characteristics
    """
    from .config_processor import process_config

    if config is None:
        config = process_config(config_path)
    rule_config = config["RULE"]
    seed = config.get("SEED", 42)
    num_products = rule_config.get("NUM_PRODUCTS", 100)
    if seed is not None:
        random.seed(seed)
    products: List[Dict] = []
    for i in range(num_products):
        category = random.choice(_CATEGORIES)
        price_min, price_max = _PRICE_RANGES[category]
        price = round(random.uniform(price_min, price_max), 2)
        products.append(
            {
                "asin": generate_random_asin(),
                "category": category,
                "price": price,
            }
        )
    return pd.DataFrame(products)
