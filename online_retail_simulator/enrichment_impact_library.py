"""Library of predefined treatment effect functions for catalog enrichment.

Each function takes a sale dictionary and enrichment metadata, and returns
a modified sale dictionary with the treatment effect applied.
"""

from datetime import datetime
from typing import Dict


def quantity_boost(sale: Dict, enrichment_start: str, effect_size: float = 0.5) -> Dict:
    """
    Boost quantity sold by a percentage.
    
    Args:
        sale: Sale transaction dictionary
        enrichment_start: Start date of enrichment (YYYY-MM-DD)
        effect_size: Percentage increase in quantity (default: 0.5 for 50% boost)
    
    Returns:
        Modified sale dictionary with boosted quantity and revenue
    """
    sale_date = datetime.strptime(sale['date'], '%Y-%m-%d')
    start_date = datetime.strptime(enrichment_start, '%Y-%m-%d')
    
    if sale_date >= start_date:
        original_quantity = sale['quantity']
        sale['quantity'] = int(original_quantity * (1 + effect_size))
        sale['revenue'] = round(sale['quantity'] * sale['unit_price'], 2)
    
    return sale


def probability_boost(sale: Dict, enrichment_start: str, effect_size: float = 0.5) -> Dict:
    """
    Boost sale probability (simulated by quantity increase as proxy).
    
    Note: Since sales are already generated, we simulate probability boost
    by increasing quantity on successful sales.
    
    Args:
        sale: Sale transaction dictionary
        enrichment_start: Start date of enrichment (YYYY-MM-DD)
        effect_size: Percentage increase in sale likelihood (default: 0.5)
    
    Returns:
        Modified sale dictionary
    """
    # For existing sales, probability boost is reflected in quantity
    return quantity_boost(sale, enrichment_start, effect_size)


def combined_boost(sale: Dict, enrichment_start: str, effect_size: float = 0.5) -> Dict:
    """
    Combined treatment effect with ramp-up period.
    
    Gradually increases effect over 7 days after enrichment starts, then
    maintains full effect.
    
    Args:
        sale: Sale transaction dictionary
        enrichment_start: Start date of enrichment (YYYY-MM-DD)
        effect_size: Maximum percentage increase (default: 0.5 for 50% boost)
    
    Returns:
        Modified sale dictionary with ramped treatment effect
    """
    sale_date = datetime.strptime(sale['date'], '%Y-%m-%d')
    start_date = datetime.strptime(enrichment_start, '%Y-%m-%d')
    
    if sale_date >= start_date:
        days_since_start = (sale_date - start_date).days
        ramp_factor = min(1.0, days_since_start / 7.0)  # 7-day ramp-up
        adjusted_effect = effect_size * ramp_factor
        
        original_quantity = sale['quantity']
        sale['quantity'] = int(original_quantity * (1 + adjusted_effect))
        sale['revenue'] = round(sale['quantity'] * sale['unit_price'], 2)
    
    return sale
