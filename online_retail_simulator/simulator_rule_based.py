"""Rule-based product and sales generators combined in one module."""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Product generation constants
CATEGORIES = [
    "Electronics",
    "Clothing",
    "Home & Garden",
    "Books",
    "Sports & Outdoors",
    "Toys & Games",
    "Food & Beverage",
    "Health & Beauty"
]

PRODUCT_NAMES = {
    "Electronics": ["Laptop", "Smartphone", "Tablet", "Headphones", "Monitor", "Keyboard", "Mouse", "Webcam"],
    "Clothing": ["T-Shirt", "Jeans", "Jacket", "Sweater", "Dress", "Shorts", "Hoodie", "Socks"],
    "Home & Garden": ["Chair", "Table", "Lamp", "Rug", "Curtains", "Vase", "Mirror", "Clock"],
    "Books": ["Novel", "Textbook", "Cookbook", "Biography", "Comic", "Magazine", "Journal", "Guide"],
    "Sports & Outdoors": ["Ball", "Bike", "Tent", "Backpack", "Yoga Mat", "Weights", "Running Shoes", "Water Bottle"],
    "Toys & Games": ["Board Game", "Puzzle", "Action Figure", "Doll", "Building Blocks", "Card Game", "Stuffed Animal", "Remote Car"],
    "Food & Beverage": ["Coffee", "Tea", "Snacks", "Chocolate", "Juice", "Cookies", "Nuts", "Energy Bar"],
    "Health & Beauty": ["Shampoo", "Lotion", "Soap", "Toothpaste", "Perfume", "Makeup", "Vitamins", "Sunscreen"]
}

PRICE_RANGES = {
    "Electronics": (50, 1500),
    "Clothing": (15, 200),
    "Home & Garden": (20, 500),
    "Books": (10, 60),
    "Sports & Outdoors": (15, 300),
    "Toys & Games": (10, 100),
    "Food & Beverage": (5, 50),
    "Health & Beauty": (8, 80)
}


def generate_product_data(n_products: int = 100, seed: int = None) -> List[Dict]:
    """
    Generate synthetic product data.
    
    Args:
        n_products: Number of products to generate (default: 100)
        seed: Random seed for reproducibility (default: None)
    
    Returns:
        List of product dictionaries with id, name, category, and price
    """
    if seed is not None:
        random.seed(seed)
    
    products: List[Dict] = []
    for i in range(n_products):
        category = random.choice(CATEGORIES)
        product_name = random.choice(PRODUCT_NAMES[category])
        price_min, price_max = PRICE_RANGES[category]
        price = round(random.uniform(price_min, price_max), 2)
        products.append({
            "product_id": f"PROD{i+1:04d}",
            "name": product_name,
            "category": category,
            "price": price
        })
    return products


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
        products: List of product dictionaries
        date_start: Start date in "YYYY-MM-DD" format
        date_end: End date in "YYYY-MM-DD" format
        seed: Random seed for reproducibility (default: None)
        sale_probability: Probability of a sale for each product-day (default: 0.7)
    
    Returns:
        List of sales transaction dictionaries
    """
    if seed is not None:
        random.seed(seed)
    
    start_date = datetime.strptime(date_start, "%Y-%m-%d")
    end_date = datetime.strptime(date_end, "%Y-%m-%d")
    
    sales: List[Dict] = []
    transaction_counter = 0
    current_date = start_date
    while current_date <= end_date:
        for product in products:
            if random.random() < sale_probability:
                transaction_counter += 1
                quantity = random.choices([1, 2, 3, 4, 5], weights=[50, 25, 15, 7, 3])[0]
                revenue = round(product["price"] * quantity, 2)
                sales.append({
                    "transaction_id": f"TXN{transaction_counter:06d}",
                    "product_id": product["product_id"],
                    "product_name": product["name"],
                    "category": product["category"],
                    "quantity": quantity,
                    "unit_price": product["price"],
                    "revenue": revenue,
                    "date": current_date.strftime("%Y-%m-%d")
                })
        current_date += timedelta(days=1)
    
    return sales
