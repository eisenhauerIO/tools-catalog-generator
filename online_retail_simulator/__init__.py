"""Online Retail Simulator - Generate synthetic retail data for experimentation."""

from .simulator import simulate
from .simulator_rule_based import simulate_rule_based, generate_product_data, generate_sales_data
from .simulator_synthesizer_based import train_synthesizer, simulate_synthesizer_based

__version__ = "0.1.0"
__all__ = [
    "simulate",
    "simulate_rule_based",
    "simulate_synthesizer_based",
    "generate_product_data",
    "generate_sales_data",
    "train_synthesizer",
]
