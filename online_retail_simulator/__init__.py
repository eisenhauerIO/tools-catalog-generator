"""Online Retail Simulator - Generate synthetic retail data for experimentation."""

from .simulator import generate_products, generate_sales, save_to_json, simulate
from .monte_carlo_sampler import train_synthesizer, generate_sample

__version__ = "0.1.0"
__all__ = [
    "simulate", 
    "generate_products", 
    "generate_sales", 
    "save_to_json",
    "train_synthesizer",
    "generate_sample",
]
