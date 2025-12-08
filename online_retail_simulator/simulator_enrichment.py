"""Enrichment module for applying catalog enrichment treatments to sales data."""

import random
import importlib
import json
import copy
from pathlib import Path
from typing import List, Dict, Callable


def assign_enrichment(
    products: List[Dict],
    fraction: float,
    seed: int = None
) -> List[Dict]:
    """
    Assign enrichment treatment to a fraction of products.
    
    Args:
        products: List of product dictionaries
        fraction: Fraction of products to enrich (0.0 to 1.0)
        seed: Random seed for reproducibility
    
    Returns:
        List of products with added 'enriched' boolean field
    """
    if seed is not None:
        random.seed(seed)
    
    # Create copy to avoid modifying original
    enriched_products = copy.deepcopy(products)
    
    # Randomly select products for enrichment
    n_enriched = int(len(products) * fraction)
    enriched_indices = random.sample(range(len(products)), n_enriched)
    
    # Add enrichment field
    for i, product in enumerate(enriched_products):
        product['enriched'] = i in enriched_indices
    
    return enriched_products


def load_effect_function(module_name: str, function_name: str) -> Callable:
    """
    Load treatment effect function from module.
    
    Args:
        module_name: Name of module (e.g., 'enrichment_impact_library' or 'my_custom_effects')
        function_name: Name of function within module
    
    Returns:
        Treatment effect function
    """
    # Try to import from online_retail_simulator package first
    try:
        module = importlib.import_module(f'online_retail_simulator.{module_name}')
    except (ImportError, ModuleNotFoundError):
        # Fall back to importing as standalone module
        module = importlib.import_module(module_name)
    
    return getattr(module, function_name)


def apply_enrichment_to_sales(
    sales: List[Dict],
    enriched_products: List[Dict],
    enrichment_start: str,
    effect_function: Callable,
    effect_size: float = 0.5
) -> List[Dict]:
    """
    Apply enrichment treatment effect to sales data.
    
    Args:
        sales: List of sale transaction dictionaries
        enriched_products: List of products with 'enriched' field
        enrichment_start: Start date of enrichment (YYYY-MM-DD)
        effect_function: Treatment effect function to apply
        effect_size: Magnitude of effect (interpretation depends on function)
    
    Returns:
        List of modified sales with treatment effect applied
    """
    # Create lookup for enriched products
    enriched_ids = {p['product_id'] for p in enriched_products if p.get('enriched', False)}
    
    # Apply effect to sales of enriched products
    treated_sales = []
    for sale in sales:
        sale_copy = copy.deepcopy(sale)
        
        if sale_copy['product_id'] in enriched_ids:
            # Apply treatment effect function
            sale_copy = effect_function(
                sale_copy,
                enrichment_start=enrichment_start,
                effect_size=effect_size
            )
        
        treated_sales.append(sale_copy)
    
    return treated_sales
