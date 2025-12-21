"""Library of predefined treatment effect functions for catalog enrichment.

Each function takes a sale dictionary and enrichment metadata, and returns
a modified sale dictionary with the treatment effect applied.
"""

from datetime import datetime


def quantity_boost(sales: list, **kwargs) -> list:
    """
    Boost ordered units by a percentage for enriched products.

    Args:
        sales: List of sale transaction dictionaries
        **kwargs: Parameters including:
            - effect_size: Percentage increase in ordered units (default: 0.5 for 50% boost)
            - enrichment_fraction: Fraction of products to enrich (default: 0.3)
            - enrichment_start: Start date of enrichment (default: "2024-11-15")
            - seed: Random seed for product selection (default: 42)

    Returns:
        List of modified sale dictionaries with treatment applied
    """
    import copy
    import random

    effect_size = kwargs.get("effect_size", 0.5)
    enrichment_fraction = kwargs.get("enrichment_fraction", 0.3)
    enrichment_start = kwargs.get("enrichment_start", "2024-11-15")
    seed = kwargs.get("seed", 42)

    # Set seed for reproducibility
    if seed is not None:
        random.seed(seed)

    # Get unique products and select fraction for enrichment
    unique_products = list(set(sale["product_id"] for sale in sales))
    n_enriched = int(len(unique_products) * enrichment_fraction)
    enriched_product_ids = set(random.sample(unique_products, n_enriched))

    # Apply treatment to enriched products after start date
    treated_sales = []
    start_date = datetime.strptime(enrichment_start, "%Y-%m-%d")

    for sale in sales:
        sale_copy = copy.deepcopy(sale)
        sale_date = datetime.strptime(sale_copy["date"], "%Y-%m-%d")

        # Apply boost if product is enriched and date is after start
        if sale_copy["product_id"] in enriched_product_ids and sale_date >= start_date:
            original_quantity = sale_copy["ordered_units"]
            sale_copy["ordered_units"] = int(original_quantity * (1 + effect_size))
            unit_price = sale_copy.get("unit_price", sale_copy.get("price"))
            sale_copy["revenue"] = round(sale_copy["ordered_units"] * unit_price, 2)

        treated_sales.append(sale_copy)

    return treated_sales


def probability_boost(sales: list, **kwargs) -> list:
    """
    Boost sale probability (simulated by ordered units increase as proxy).

    Note: Since sales are already generated, we simulate probability boost
    by increasing ordered units on successful sales.

    Args:
        sales: List of sale transaction dictionaries
        **kwargs: Same parameters as quantity_boost

    Returns:
        List of modified sale dictionaries
    """
    # For existing sales, probability boost is reflected in quantity
    return quantity_boost(sales, **kwargs)


def combined_boost(sales: list, **kwargs) -> list:
    """
    Combined treatment effect with ramp-up period for enriched products.

    Gradually increases effect over ramp_days after enrichment starts, then
    maintains full effect.

    Args:
        sales: List of sale transaction dictionaries
        **kwargs: Parameters including:
            - effect_size: Maximum percentage increase (default: 0.5 for 50% boost)
            - ramp_days: Number of days for ramp-up period (default: 7)
            - enrichment_fraction: Fraction of products to enrich (default: 0.3)
            - enrichment_start: Start date of enrichment (default: "2024-11-15")
            - seed: Random seed for product selection (default: 42)

    Returns:
        List of modified sale dictionaries with ramped treatment effect
    """
    import copy
    import random

    effect_size = kwargs.get("effect_size", 0.5)
    ramp_days = kwargs.get("ramp_days", 7)
    enrichment_fraction = kwargs.get("enrichment_fraction", 0.3)
    enrichment_start = kwargs.get("enrichment_start", "2024-11-15")
    seed = kwargs.get("seed", 42)

    # Set seed for reproducibility
    if seed is not None:
        random.seed(seed)

    # Get unique products and select fraction for enrichment
    unique_products = list(set(sale["product_id"] for sale in sales))
    n_enriched = int(len(unique_products) * enrichment_fraction)
    enriched_product_ids = set(random.sample(unique_products, n_enriched))

    # Apply treatment to enriched products after start date
    treated_sales = []
    start_date = datetime.strptime(enrichment_start, "%Y-%m-%d")

    for sale in sales:
        sale_copy = copy.deepcopy(sale)
        sale_date = datetime.strptime(sale_copy["date"], "%Y-%m-%d")

        # Apply ramped boost if product is enriched and date is after start
        if sale_copy["product_id"] in enriched_product_ids and sale_date >= start_date:
            days_since_start = (sale_date - start_date).days

            # Handle zero ramp_days case
            if ramp_days <= 0:
                ramp_factor = 1.0
            else:
                ramp_factor = min(1.0, days_since_start / ramp_days)

            adjusted_effect = effect_size * ramp_factor

            original_quantity = sale_copy["ordered_units"]
            sale_copy["ordered_units"] = int(original_quantity * (1 + adjusted_effect))
            unit_price = sale_copy.get("unit_price", sale_copy.get("price"))
            sale_copy["revenue"] = round(sale_copy["ordered_units"] * unit_price, 2)

        treated_sales.append(sale_copy)

    return treated_sales
