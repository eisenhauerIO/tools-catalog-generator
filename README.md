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

The simplest way to use the simulator is with a YAML configuration file:

```python
from online_retail_simulator import simulate

simulate("config.yaml")
```

### Configuration (prefix-based)

Each config chooses a simulator mode and shares common baseline settings and an output prefix.

Required keys:
- `SIMULATOR.mode`: `"rule"` or `"synthesizer"`
- `OUTPUT.dir`: where files are written
- `OUTPUT.file_prefix`: base name for generated files
- `BASELINE`: `DATE_START`, `DATE_END`, `NUM_PRODUCTS`, `SALE_PROB`

Rule-based example (baseline only):

```yaml
SIMULATOR:
  mode: rule

SEED: 42

OUTPUT:
  dir: demo/output
  file_prefix: rb_demo

RULE:
  NUM_PRODUCTS: 50
  DATE_START: "2024-11-01"
  DATE_END: "2024-11-30"
  SALE_PROB: 0.7
```

Synthesizer example:

```yaml
SIMULATOR:
  mode: synthesizer

SEED: 42

OUTPUT:
  dir: demo/output_mc
  file_prefix: sdv_demo

RULE:
  NUM_PRODUCTS: 30
  DATE_START: "2024-11-01"
  DATE_END: "2024-11-15"
  SALE_PROB: 0.7

SYNTHESIZER:
  SYNTHESIZER_TYPE: gaussian_copula
  DEFAULT_PRODUCTS_ROWS: 30
  DEFAULT_SALES_ROWS: 5000
```

Derived filenames (under `OUTPUT.dir`):
- Rule: `<prefix>_products.json`, `<prefix>_sales.json` (enrichment, if configured under `RULE.ENRICHMENT`: `<prefix>_enriched.json`, `<prefix>_factual.json`, `<prefix>_counterfactual.json`).
- Synthesizer: `<prefix>_model_products.pkl`, `<prefix>_model_sales.pkl`, `<prefix>_mc_products.json`, `<prefix>_mc_sales.json`.

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

This generates sample product and sales data based on `demo/config_rule.yaml`, saving them to `demo/output/products.json` and `demo/output/sales.json`.

## Features

- **Simple product generation**: Creates products with ID, name, category, and price across 8 categories
- **Realistic daily sales data**: Generates transactions with dates, quantities, and revenue
- **Stochastic sales patterns**: Not every product sells every day (70% probability by default)
- **Reproducible**: Use seed parameter for deterministic output
- **JSON export**: Easy data export for use in other tools
- **Config-driven**: Single entry point with YAML configuration

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
