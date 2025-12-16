"""Example custom enrichment effects for demonstration."""

import copy
import random
from datetime import datetime
from typing import Dict, List


def price_discount(sales: List[Dict], **kwargs) -> List[Dict]:
    """
    Apply price discount to enriched products.

    Args:
        sales: List of sale transaction dictionaries
        **kwargs: Parameters including:
            - discount_percent: Percentage discount (default: 0.2 for 20% off)
            - enrichment_fraction: Fraction of products to enrich (default: 0.3)
            - enrichment_start: Start date of enrichment (default: "2024-11-15")
            - seed: Random seed for product selection (default: 42)

    Returns:
        List of modified sale dictionaries with price discount applied
    """
    discount_percent = kwargs.get("discount_percent", 0.2)
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

    # Apply discount to enriched products after start date
    treated_sales = []
    start_date = datetime.strptime(enrichment_start, "%Y-%m-%d")

    for sale in sales:
        sale_copy = copy.deepcopy(sale)
        sale_date = datetime.strptime(sale_copy["date"], "%Y-%m-%d")

        # Apply discount if product is enriched and date is after start
        if sale_copy["product_id"] in enriched_product_ids and sale_date >= start_date:
            unit_price = sale_copy.get("unit_price", sale_copy.get("price"))
            discounted_price = unit_price * (1 - discount_percent)

            # Update price fields
            if "unit_price" in sale_copy:
                sale_copy["unit_price"] = round(discounted_price, 2)
            if "price" in sale_copy:
                sale_copy["price"] = round(discounted_price, 2)

            # Recalculate revenue
            sale_copy["revenue"] = round(sale_copy["quantity"] * discounted_price, 2)

        treated_sales.append(sale_copy)

    return treated_sales


def category_boost(sales: List[Dict], **kwargs) -> List[Dict]:
    """
    Boost sales for specific product categories.

    Args:
        sales: List of sale transaction dictionaries
        **kwargs: Parameters including:
            - target_categories: List of categories to boost (default: ["Electronics"])
            - boost_factor: Multiplier for quantity (default: 1.5)
            - enrichment_start: Start date of enrichment (default: "2024-11-15")

    Returns:
        List of modified sale dictionaries with category boost applied
    """
    target_categories = kwargs.get("target_categories", ["Electronics"])
    boost_factor = kwargs.get("boost_factor", 1.5)
    enrichment_start = kwargs.get("enrichment_start", "2024-11-15")

    treated_sales = []
    start_date = datetime.strptime(enrichment_start, "%Y-%m-%d")

    for sale in sales:
        sale_copy = copy.deepcopy(sale)
        sale_date = datetime.strptime(sale_copy["date"], "%Y-%m-%d")

        # Apply boost if category matches and date is after start
        if (sale_copy.get("category") in target_categories and
            sale_date >= start_date):

            original_quantity = sale_copy["quantity"]
            sale_copy["quantity"] = int(original_quantity * boost_factor)

            # Recalculate revenue
            unit_price = sale_copy.get("unit_price", sale_copy.get("price"))
            sale_copy["revenue"] = round(sale_copy["quantity"] * unit_price, 2)

        treated_sales.append(sale_copy)

    return treated_sales


def seasonal_multiplier(sales: List[Dict], **kwargs) -> List[Dict]:
    """
    Apply seasonal multiplier based on date.

    Args:
        sales: List of sale transaction dictionaries
        **kwargs: Parameters including:
            - peak_months: List of peak months (1-12) (default: [11, 12])
            - peak_multiplier: Multiplier during peak months (default: 2.0)
            - enrichment_fraction: Fraction of products to enrich (default: 0.4)
            - seed: Random seed for product selection (default: 42)

    Returns:
        List of modified sale dictionaries with seasonal effects applied
    """
    peak_months = kwargs.get("peak_months", [11, 12])  # Nov, Dec
    peak_multiplier = kwargs.get("peak_multiplier", 2.0)
    enrichment_fraction = kwargs.get("enrichment_fraction", 0.4)
    seed = kwargs.get("seed", 42)

    # Set seed for reproducibility
    if seed is not None:
        random.seed(seed)

    # Get unique products and select fraction for enrichment
    unique_products = list(set(sale["product_id"] for sale in sales))
    n_enriched = int(len(unique_products) * enrichment_fraction)
    enriched_product_ids = set(random.sample(unique_products, n_enriched))

    treated_sales = []

    for sale in sales:
        sale_copy = copy.deepcopy(sale)
        sale_date = datetime.strptime(sale_copy["date"], "%Y-%m-%d")

        # Apply seasonal boost if product is enriched and in peak month
        if (sale_copy["product_id"] in enriched_product_ids and
            sale_date.month in peak_months):

            original_quantity = sale_copy["quantity"]
            sale_copy["quantity"] = int(original_quantity * peak_multiplier)

            # Recalculate revenue
            unit_price = sale_copy.get("unit_price", sale_copy.get("price"))
            sale_copy["revenue"] = round(sale_copy["quantity"] * unit_price, 2)

        treated_sales.append(sale_copy)

    return treated_sales
