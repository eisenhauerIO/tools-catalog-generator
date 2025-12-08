"""Generate synthetic sales data."""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional


def generate_sales_data(
    products: List[Dict],
    date_start: str,
    date_end: str,
    seed: Optional[int] = None,
    sale_probability: float = 0.7
) -> List[Dict]:
    """
    Generate synthetic daily sales transactions from product data.
    
    Generates one potential transaction per product per day. Each product-day
    combination has a probability of generating a sale (default 70%).
    
    Args:
        products: List of product dictionaries (from simulator_product_data)
        date_start: Start date in "YYYY-MM-DD" format
        date_end: End date in "YYYY-MM-DD" format
        seed: Random seed for reproducibility (default: None)
        sale_probability: Probability of a sale occurring for each product-day (default: 0.7)
    
    Returns:
        List of sales transaction dictionaries
    """
    if seed is not None:
        random.seed(seed)
    
    # Parse dates
    start_date = datetime.strptime(date_start, "%Y-%m-%d")
    end_date = datetime.strptime(date_end, "%Y-%m-%d")
    
    sales = []
    transaction_counter = 0
    
    # Iterate through each day in the range
    current_date = start_date
    while current_date <= end_date:
        # For each product, randomly decide if there's a sale
        for product in products:
            # Random chance of sale occurring
            if random.random() < sale_probability:
                transaction_counter += 1
                
                # Generate quantity (favor smaller quantities)
                quantity = random.choices(
                    [1, 2, 3, 4, 5],
                    weights=[50, 25, 15, 7, 3]
                )[0]
                
                # Calculate revenue
                revenue = round(product["price"] * quantity, 2)
                
                transaction = {
                    "transaction_id": f"TXN{transaction_counter:06d}",
                    "product_id": product["product_id"],
                    "product_name": product["name"],
                    "category": product["category"],
                    "quantity": quantity,
                    "unit_price": product["price"],
                    "revenue": revenue,
                    "date": current_date.strftime("%Y-%m-%d")
                }
                sales.append(transaction)
        
        # Move to next day
        current_date += timedelta(days=1)
    
    return sales
