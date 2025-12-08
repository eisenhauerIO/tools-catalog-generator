# Online Retail Simulator

A lightweight Python package for simulating realistic retail data for experimentation and causal inference in e-commerce contexts.

## Overview

The Online Retail Simulator generates synthetic product catalogs and daily sales transactions with reproducible random seeds. Perfect for testing, demos, and teaching data science concepts without exposing real business data.

## Installation

For development:

```bash
pip install -e ".[dev]"
```

## Quick Start

The simplest way to use the simulator is with a JSON configuration file:

```python
from online_retail_simulator import simulate

simulate("config.json")
```

### Configuration File

Create a `config.json` file with the following structure:

```json
{
  "SEED": 42,
  "NUM_PRODUCTS": 50,
  "DATE_START": "2024-11-01",
  "DATE_END": "2024-11-30",
  "OUTPUT_DIR": "output",
  "PRODUCTS_FILE": "products.json",
  "SALES_FILE": "sales.json"
}
```

**Configuration Parameters:**
- `SEED`: Random seed for reproducibility
- `NUM_PRODUCTS`: Number of products to generate
- `DATE_START`: Start date in "YYYY-MM-DD" format
- `DATE_END`: End date in "YYYY-MM-DD" format
- `OUTPUT_DIR`: Directory for output files
- `PRODUCTS_FILE`: Filename for products JSON
- `SALES_FILE`: Filename for sales JSON

### Programmatic Usage

You can also use the individual functions directly:

```python
from online_retail_simulator import generate_products, generate_sales, save_to_json

# Generate product catalog with seed for reproducibility
products = generate_products(n_products=50, seed=42)

# Generate daily sales transactions over date range
sales = generate_sales(
    products=products,
    date_start="2024-11-01",
    date_end="2024-11-30",
    seed=42
)

# Export to JSON
save_to_json(products, "products.json")
save_to_json(sales, "sales.json")
```

## Demo

Run the example script to see the simulator in action:

```bash
python demo/example.py
```

This generates sample product and sales data based on `demo/config.json`, saving them to `demo/output/products.json` and `demo/output/sales.json`.

## Features

- **Simple product generation**: Creates products with ID, name, category, and price across 8 categories
- **Realistic daily sales data**: Generates transactions with dates, quantities, and revenue
- **Stochastic sales patterns**: Not every product sells every day (70% probability by default)
- **Reproducible**: Use seed parameter for deterministic output
- **JSON export**: Easy data export for use in other tools
- **Config-driven**: Single entry point with JSON configuration

## Data Structure

### Products
```json
{
  "product_id": "PROD0001",
  "name": "Laptop",
  "category": "Electronics",
  "price": 899.99
}
```

### Sales
```json
{
  "transaction_id": "TXN000001",
  "product_id": "PROD0023",
  "product_name": "Smartphone",
  "category": "Electronics",
  "quantity": 2,
  "unit_price": 599.99,
  "revenue": 1199.98,
  "date": "2024-11-15"
}
```

## Requirements

- Python 3.8+

## License

MIT

