# Enrichment Registration Examples

This directory contains examples demonstrating how to register and use custom enrichment functions with the Online Retail Simulator.

## Files

- `custom_effects.py` - Example custom enrichment functions
- `registration_example.py` - Complete demo of registration and usage
- `config_custom_discount.yaml` - Config using price discount effect
- `config_seasonal.yaml` - Config using seasonal multiplier effect

## Custom Effects Included

### `price_discount`
Applies percentage price discounts to selected products after enrichment start date.

**Parameters:**
- `discount_percent` - Percentage discount (0.2 = 20% off)
- `enrichment_fraction` - Fraction of products to discount
- `enrichment_start` - Start date for discount
- `seed` - Random seed for product selection

### `category_boost`
Boosts sales quantity for specific product categories.

**Parameters:**
- `target_categories` - List of categories to boost
- `boost_factor` - Quantity multiplier
- `enrichment_start` - Start date for boost

### `seasonal_multiplier`
Applies seasonal sales multipliers during peak months.

**Parameters:**
- `peak_months` - List of peak months (1-12)
- `peak_multiplier` - Quantity multiplier during peak
- `enrichment_fraction` - Fraction of products affected
- `seed` - Random seed for product selection

## Usage

### 1. Direct Function Registration

```python
from online_retail_simulator import register_enrichment_function

def my_effect(sales, **kwargs):
    # Custom logic here
    return modified_sales

register_enrichment_function("my_effect", my_effect)
```

### 2. Module Registration

```python
from online_retail_simulator import register_enrichment_module

# Register all functions from a module
register_enrichment_module("custom_effects")
```

### 3. Use in Config

```yaml
IMPACT:
  FUNCTION: "price_discount"  # Use registered function name
  PARAMS:
    discount_percent: 0.15
    enrichment_fraction: 0.3
```

### 4. Apply Enrichment

```python
from online_retail_simulator import enrich, simulate

# Generate data
sales_df = simulate("../config_rule.yaml")

# Apply custom enrichment
enriched_df = enrich("config_custom_discount.yaml", sales_df)
```

## Running the Demo

```bash
cd demo/enrichment
python registration_example.py
```

This will demonstrate:
- Registering functions directly and from modules
- Using registered functions in enrichment configs
- Comparing results before and after enrichment

## Function Requirements

Custom enrichment functions must:
- Accept `sales` as first parameter (list of sale dictionaries)
- Accept `**kwargs` for configuration parameters
- Return modified list of sale dictionaries
- Preserve the structure of sale records
