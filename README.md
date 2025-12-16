# Online Retail Simulator

Generate synthetic retail data for testing, demos, and experimentation without exposing real business data.

## Quick Start

### 1. Install
```bash
# Basic installation
pip install -e .

# With ML-based generation (optional)
pip install -e ".[synthesizer]"

# For development
pip install -e ".[dev]"
```

### 2. Run Demo
```bash
python demo/example.py
```

### 3. Use in Code
```python
from online_retail_simulator import simulate

# Generate data using config file
sales_df = simulate("demo/config_rule.yaml")
print(f"Generated {len(sales_df)} sales records")
```

## Configuration

Create a YAML config file:

```yaml
SEED: 42

OUTPUT:
  DIR: output
  FILE_PREFIX: my_data

RULE:
  NUM_PRODUCTS: 50
  DATE_START: "2024-11-01"
  DATE_END: "2024-11-30"
  SALE_PROB: 0.7
```

For ML-based generation:

```yaml
SEED: 42

OUTPUT:
  DIR: output
  FILE_PREFIX: my_data

SYNTHESIZER:
  SYNTHESIZER_TYPE: gaussian_copula
  DEFAULT_PRODUCTS_ROWS: 30
  DEFAULT_SALES_ROWS: 5000
```

## Programmatic Usage

```python
from online_retail_simulator import simulate

# One-step generation (recommended)
sales_df = simulate("config.yaml")

# Or step-by-step
from online_retail_simulator import simulate_characteristics, simulate_metrics

products_df = simulate_characteristics("config.yaml")
sales_df = simulate_metrics(products_df, "config.yaml")
```
## Enrichment (Treatment Effects)

Apply treatment effects to simulate catalog enrichment experiments. Effects are applied to:
- **Selected products only**: A fraction of products receive enrichment (default 50%)
- **Date-based**: Effects only apply to sales on/after the enrichment start date
- **Targeted impact**: Only sales of enriched products are modified

```yaml
SEED: 42

OUTPUT:
  DIR: output
  FILE_PREFIX: enriched_data

SYNTHESIZER:
  SYNTHESIZER_TYPE: gaussian_copula
  DEFAULT_PRODUCTS_ROWS: 30
  DEFAULT_SALES_ROWS: 5000

# Apply quantity boost effect
EFFECT: "quantity_boost:0.5"

# Optional: Control enrichment parameters
ENRICHMENT_FRACTION: 0.3  # 30% of products get enriched
ENRICHMENT_START: "2024-11-15"  # Effects start from this date
```

### Available Effects

- `quantity_boost:0.5` - Increase quantity sold by 50%
- `probability_boost:0.3` - Increase sale probability by 30%
- `combined_boost` - Gradual ramp-up effect with custom parameters

### Custom Effect Parameters

```yaml
EFFECT:
  function: "combined_boost"
  params:
    effect_size: 0.5
    ramp_days: 7
```

### Programmatic Enrichment

```python
from online_retail_simulator.enrichment_application import enrich

# Apply enrichment to existing sales data
enriched_df = enrich("enrichment_config.yaml", sales_df)
```

## Features

- **Two modes**: Rule-based (simple) or ML-based (requires SDV)
- **Treatment effects**: Simulate catalog enrichment experiments
- **Reproducible**: Seed-controlled random generation
- **Realistic data**: 8 product categories, daily sales patterns
- **DataFrame output**: Returns pandas DataFrames
- **Python 3.8+**: Broad compatibility

## Data Structure

### Products DataFrame
```python
# Columns: asin, category, price
{
  "asin": "BRPOIG8F1C",
  "category": "Electronics",
  "price": 899.99
}
```

### Sales DataFrame
```python
# Columns: asin, category, price, date, quantity, revenue
{
  "asin": "BRPOIG8F1C",
  "category": "Electronics",
  "price": 899.99,
  "date": "2024-11-15",
  "quantity": 2,
  "revenue": 1799.98
}
```

## License

MIT
