"""Rule-based product and sales generators combined in one module."""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple

import pandas as pd

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


def simulate_rule_based(config_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Main entry point: run rule-based simulation from JSON configuration file.
    
    Supports two modes:
    1. Baseline only: Generates products and sales
    2. With enrichment: Generates baseline + applies treatment effect
    
    Args:
        config_path: Path to JSON configuration file
    
    Returns:
        Tuple of (products_df, sales_df) as pandas DataFrames
        
    Configuration structure:
        Flat config (baseline only):
            - SEED, NUM_PRODUCTS, DATE_START, DATE_END, OUTPUT_DIR,
              PRODUCTS_FILE, SALES_FILE
        
        Hierarchical config (with enrichment):
            - SEED, OUTPUT_DIR (shared)
            - BASELINE: {NUM_PRODUCTS, DATE_START, DATE_END, PRODUCTS_FILE, SALES_FILE}
            - ENRICHMENT: {START_DATE, FRACTION, EFFECT_MODULE, EFFECT_FUNCTION,
                          EFFECT_SIZE, PRODUCTS_FILE, SALES_FACTUAL_FILE,
                          SALES_COUNTERFACTUAL_FILE}
    """
    # Lazy import to avoid circular dependencies
    from .enrichment_application import assign_enrichment, load_effect_function, apply_enrichment_to_sales, parse_effect_spec
    from .config_processor import process_config
    
    def save_to_json(data: List[Dict], filepath: str, indent: int = 2) -> None:
        """Save data to JSON file."""
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=indent)
        print(f"Data saved to {filepath}")
    
    # Load and process configuration with defaults
    config = process_config(config_path)
    
    # Check if hierarchical config (with BASELINE section)
    # Only enable enrichment if START_DATE is provided
    has_enrichment = (
        "ENRICHMENT" in config and 
        config["ENRICHMENT"].get("START_DATE")
    )
    
    if "BASELINE" in config:
        # Hierarchical config
        seed = config.get("SEED", 42)
        output_dir = config.get("OUTPUT_DIR", "output")
        baseline_config = config["BASELINE"]
        
        num_products = baseline_config.get("NUM_PRODUCTS", 100)
        date_start = baseline_config.get("DATE_START")
        date_end = baseline_config.get("DATE_END")
        products_file = baseline_config.get("PRODUCTS_FILE", "products.json")
        sales_file = baseline_config.get("SALES_FILE", "sales.json")
    else:
        # Flat config (legacy support)
        seed = config.get("SEED", 42)
        num_products = config.get("NUM_PRODUCTS", 100)
        date_start = config.get("DATE_START")
        date_end = config.get("DATE_END")
        output_dir = config.get("OUTPUT_DIR", "output")
        products_file = config.get("PRODUCTS_FILE", "products.json")
        sales_file = config.get("SALES_FILE", "sales.json")
    
    if not date_start or not date_end:
        raise ValueError("Configuration must include DATE_START and DATE_END")
    
    print("=" * 60)
    print("Online Retail Simulator")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  Seed:         {seed}")
    print(f"  Products:     {num_products}")
    print(f"  Date Range:   {date_start} to {date_end}")
    print(f"  Output Dir:   {output_dir}")
    if has_enrichment:
        print(f"  Mode:         Baseline + Enrichment")
    
    # Generate baseline products
    print(f"\nGenerating {num_products} products...")
    products = generate_product_data(n_products=num_products, seed=seed)
    print(f"✓ Generated {len(products)} products")
    
    # Generate baseline sales
    print(f"\nGenerating baseline sales transactions...")
    sales = generate_sales_data(
        products=products,
        date_start=date_start,
        date_end=date_end,
        seed=seed
    )
    print(f"✓ Generated {len(sales)} baseline transactions")
    
    # Save baseline outputs
    print(f"\nSaving baseline data to {output_dir}/...")
    products_path = f"{output_dir}/{products_file}"
    sales_path = f"{output_dir}/{sales_file}"
    
    save_to_json(products, products_path)
    save_to_json(sales, sales_path)
    
    # Apply enrichment if configured
    if has_enrichment:
        enrichment_config = config["ENRICHMENT"]
        
        enrichment_start = enrichment_config.get("START_DATE")
        enrichment_fraction = enrichment_config.get("FRACTION", 0.5)
        effect_spec = enrichment_config.get("EFFECT", "quantity_boost:0.5")
        
        enriched_products_file = enrichment_config.get("PRODUCTS_FILE", "products_enriched.json")
        factual_sales_file = enrichment_config.get("SALES_FACTUAL_FILE", "sales_factual.json")
        counterfactual_sales_file = enrichment_config.get("SALES_COUNTERFACTUAL_FILE", "sales_counterfactual.json")
        
        if not enrichment_start:
            raise ValueError("ENRICHMENT configuration must include START_DATE")
        
        # Parse EFFECT specification
        effect_module, effect_function_name, effect_params = parse_effect_spec(effect_spec)
        
        print(f"\n" + "=" * 60)
        print("Applying Enrichment Treatment")
        print("=" * 60)
        print(f"  Start Date:   {enrichment_start}")
        print(f"  Fraction:     {enrichment_fraction:.0%}")
        print(f"  Effect:       {effect_module}.{effect_function_name}")
        print(f"  Params:       {effect_params}")
        
        # Assign enrichment treatment
        print(f"\nAssigning enrichment to {enrichment_fraction:.0%} of products...")
        enriched_products = assign_enrichment(products, enrichment_fraction, seed)
        n_enriched = sum(1 for p in enriched_products if p.get('enriched', False))
        print(f"✓ Assigned enrichment to {n_enriched} products")
        
        # Load effect function
        print(f"\nLoading treatment effect function...")
        effect_function = load_effect_function(effect_module, effect_function_name)
        print(f"✓ Loaded {effect_function_name} from {effect_module}")
        
        # Apply enrichment to create factual sales
        print(f"\nApplying treatment effect to create factual sales...")
        factual_sales = apply_enrichment_to_sales(
            sales,
            enriched_products,
            enrichment_start,
            effect_function,
            **effect_params
        )
        print(f"✓ Created factual sales with {len(factual_sales)} transactions")
        
        # Counterfactual = baseline (no treatment)
        counterfactual_sales = sales
        
        # Save enrichment outputs
        print(f"\nSaving enrichment data to {output_dir}/...")
        enriched_products_path = f"{output_dir}/{enriched_products_file}"
        factual_sales_path = f"{output_dir}/{factual_sales_file}"
        counterfactual_sales_path = f"{output_dir}/{counterfactual_sales_file}"
        
        save_to_json(enriched_products, enriched_products_path)
        save_to_json(factual_sales, factual_sales_path)
        save_to_json(counterfactual_sales, counterfactual_sales_path)
        
        # Display enrichment summary
        print(f"\n" + "=" * 60)
        print("Enrichment Summary")
        print("=" * 60)
        
        factual_revenue = sum(sale["revenue"] for sale in factual_sales)
        counterfactual_revenue = sum(sale["revenue"] for sale in counterfactual_sales)
        revenue_lift = ((factual_revenue - counterfactual_revenue) / counterfactual_revenue) * 100
        
        print(f"Enriched Products:  {n_enriched} of {len(products)} ({enrichment_fraction:.0%})")
        print(f"Counterfactual Revenue: ${counterfactual_revenue:,.2f}")
        print(f"Factual Revenue:        ${factual_revenue:,.2f}")
        print(f"Revenue Lift:           {revenue_lift:.2f}%")
    
    # Display final summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    total_revenue = sum(sale["revenue"] for sale in sales)
    total_quantity = sum(sale["quantity"] for sale in sales)
    categories = set(product["category"] for product in products)
    unique_dates = len(set(sale["date"] for sale in sales))
    
    print(f"Total Products:     {len(products)}")
    print(f"Product Categories: {len(categories)}")
    print(f"Total Transactions: {len(sales)}")
    print(f"Days with Sales:    {unique_dates}")
    print(f"Total Units Sold:   {total_quantity}")
    print(f"Total Revenue:      ${total_revenue:,.2f}")
    if len(sales) > 0:
        print(f"Average Order:      ${total_revenue/len(sales):.2f}")
    
    print(f"\n✓ Simulation complete!")
    
    # Convert to DataFrames and return
    products_df = pd.DataFrame(products)
    sales_df = pd.DataFrame(sales)
    return products_df, sales_df
