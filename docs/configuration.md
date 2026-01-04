# Configuration Guide

The Online Retail Simulator uses YAML configuration files to control all aspects of data generation and enrichment. This guide documents the **actual configuration schema** as implemented in the code.

> **See Also**: For practical examples and tutorials, see the [User Guide](user-guide.md).

## Configuration Structure

All configuration files follow this hierarchical structure:

```yaml
STORAGE:                    # Optional: Output storage settings
  PATH: "output/run"        # Directory for job-based storage

RULE:                       # Rule-based mode (use RULE or SYNTHESIZER, not both)
  CHARACTERISTICS:
    FUNCTION: function_name
    PARAMS:
      # Function-specific parameters
  METRICS:
    FUNCTION: function_name
    PARAMS:
      # Function-specific parameters

SYNTHESIZER:                # ML-based mode (alternative to RULE)
  CHARACTERISTICS:
    FUNCTION: function_name
    PARAMS:
      # Function-specific parameters
  METRICS:
    FUNCTION: function_name
    PARAMS:
      # Function-specific parameters
```

## Storage Configuration

### STORAGE.PATH

Controls where simulation results are saved.

```yaml
STORAGE:
  PATH: "output/myproject"  # Base directory for job storage
```

**Behavior**:
- Each simulation creates a unique job directory under this path
- Job directories are named: `job-YYYYMMDD-HHMMSS-{uuid}`
- Contains: `products.csv`, `sales.csv`, `metadata.json`, `config.yaml`
- Default: `output/run`

## Rule-Based Configuration

Rule-based mode uses deterministic algorithms. You must specify exactly **one** of `RULE` or `SYNTHESIZER`.

### Complete Example

```yaml
STORAGE:
  PATH: "output/sim_demo"

RULE:
  CHARACTERISTICS:
    FUNCTION: simulate_characteristics_rule_based
    PARAMS:
      num_products: 50
      seed: null  # Optional: set for reproducibility

  METRICS:
    FUNCTION: simulate_metrics_rule_based
    PARAMS:
      date_start: "2024-11-01"
      date_end: "2024-11-30"
      sale_prob: 0.7
      seed: null  # Optional: set for reproducibility
      granularity: "daily"  # or "weekly"
      impression_to_visit_rate: 0.15
      visit_to_cart_rate: 0.25
      cart_to_order_rate: 0.80
```

### RULE.CHARACTERISTICS Parameters

Function: `simulate_characteristics_rule_based`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `num_products` | int | 100 | Total number of products to generate |
| `seed` | int or null | null | Random seed for reproducibility |

**Example**:
```yaml
RULE:
  CHARACTERISTICS:
    FUNCTION: simulate_characteristics_rule_based
    PARAMS:
      num_products: 200
      seed: 42
```

### RULE.METRICS Parameters

Function: `simulate_metrics_rule_based`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `date_start` | string | "2024-01-01" | Start date (YYYY-MM-DD) |
| `date_end` | string | "2024-01-31" | End date (YYYY-MM-DD) |
| `sale_prob` | float | 0.7 | Daily probability of sale per product (0.0-1.0) |
| `seed` | int or null | null | Random seed for reproducibility |
| `granularity` | string | "daily" | Time granularity: "daily" or "weekly" |
| `impression_to_visit_rate` | float | 0.15 | Funnel: impressions → visits conversion rate |
| `visit_to_cart_rate` | float | 0.25 | Funnel: visits → cart adds conversion rate |
| `cart_to_order_rate` | float | 0.80 | Funnel: cart adds → orders conversion rate |

**Example**:
```yaml
RULE:
  METRICS:
    FUNCTION: simulate_metrics_rule_based
    PARAMS:
      date_start: "2024-01-01"
      date_end: "2024-12-31"
      sale_prob: 0.6
      seed: 42
      granularity: "daily"
```

### Granularity: Daily vs Weekly

The `granularity` parameter controls output aggregation:

**Daily (default)**:
- One row per product per day
- Example: 10 products × 31 days = 310 rows

**Weekly**:
- One row per product per week (ISO week: Monday-Sunday)
- Date range auto-expanded to full week boundaries
- All funnel metrics summed across the week
- `date` column shows Monday of each week
- Example: 10 products × 5 weeks = 50 rows

**Weekly Example**:
```yaml
RULE:
  METRICS:
    FUNCTION: simulate_metrics_rule_based
    PARAMS:
      date_start: "2024-01-03"  # Expanded to 2024-01-01 (Monday)
      date_end: "2024-01-25"    # Expanded to 2024-01-28 (Sunday)
      granularity: "weekly"
      sale_prob: 0.7
```

### Funnel Conversion Rates

Control the customer journey funnel:

```
Impressions → Visits → Cart Adds → Orders
            ↓15%      ↓25%         ↓80%
```

**Example with custom funnel**:
```yaml
RULE:
  METRICS:
    FUNCTION: simulate_metrics_rule_based
    PARAMS:
      date_start: "2024-11-01"
      date_end: "2024-11-30"
      sale_prob: 0.7
      impression_to_visit_rate: 0.20  # 20% of impressions → visits
      visit_to_cart_rate: 0.30        # 30% of visits → cart adds
      cart_to_order_rate: 0.85        # 85% of cart adds → orders
```

## Synthesizer-Based Configuration

ML-based mode uses SDV (Synthetic Data Vault) for sophisticated pattern learning.

### Complete Example

```yaml
STORAGE:
  PATH: "output/ml_demo"

SYNTHESIZER:
  CHARACTERISTICS:
    FUNCTION: gaussian_copula
    PARAMS:
      training_data_path: "data/real_products.csv"  # Required
      num_rows: 100
      seed: null

  METRICS:
    FUNCTION: gaussian_copula
    PARAMS:
      training_data_path: "data/real_sales.csv"  # Required
      num_rows: 1000
      seed: null
```

### SYNTHESIZER.CHARACTERISTICS Parameters

Function: `gaussian_copula`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `training_data_path` | string | **Required** | Path to CSV file with real product data |
| `num_rows` | int | 100 | Number of synthetic products to generate |
| `seed` | int or null | null | Random seed for reproducibility |

### SYNTHESIZER.METRICS Parameters

Function: `gaussian_copula`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `training_data_path` | string | **Required** | Path to CSV file with real sales data |
| `num_rows` | int | 1000 | Number of synthetic sales records to generate |
| `seed` | int | null | Random seed for reproducibility |

## Enrichment Configuration

Enrichment configurations are separate YAML files used with the `enrich()` function.

### Structure

```yaml
IMPACT:
  FUNCTION: "function_name"
  PARAMS:
    # Function-specific parameters
```

### Built-in Enrichment Functions

#### combined_boost

Gradual rollout with partial treatment (most realistic).

```yaml
IMPACT:
  FUNCTION: "combined_boost"
  PARAMS:
    effect_size: 0.5              # 50% boost in ordered_units
    ramp_days: 7                  # Gradual ramp-up over 7 days
    enrichment_fraction: 0.3      # 30% of products get enriched
    enrichment_start: "2024-11-15"  # Start date
    seed: 42                      # Reproducible product selection
```

**Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `effect_size` | float | 0.5 | Maximum boost (0.5 = 50% increase) |
| `ramp_days` | int | 7 | Days for effect to reach full strength |
| `enrichment_fraction` | float | 0.3 | Fraction of products to enrich (0.0-1.0) |
| `enrichment_start` | string | "2024-11-15" | Start date (YYYY-MM-DD) |
| `seed` | int | 42 | Random seed for product selection |

**Behavior**:
- Selects random fraction of products for enrichment
- Effect ramps up linearly over `ramp_days`
- After ramp period, full `effect_size` is applied
- Increases `ordered_units` for enriched products
- Recalculates `revenue` = `ordered_units` × `price`

#### quantity_boost

Simple multiplicative boost (no ramp-up).

```yaml
IMPACT:
  FUNCTION: "quantity_boost"
  PARAMS:
    effect_size: 0.5
    enrichment_fraction: 0.3
    enrichment_start: "2024-11-15"
    seed: 42
```

**Parameters**: Same as `combined_boost` except no `ramp_days`.

**Behavior**: Immediate full effect on enrichment start date.

#### probability_boost

Alias for `quantity_boost` (probability reflected in quantity for existing sales).

```yaml
IMPACT:
  FUNCTION: "probability_boost"
  PARAMS:
    effect_size: 0.5
    enrichment_fraction: 0.3
    enrichment_start: "2024-11-15"
    seed: 42
```

## Product Details Configuration

Product details generation adds titles, descriptions, brands, and features to products created by `simulate_characteristics()`.

### Structure

```yaml
PRODUCT_DETAILS:
  FUNCTION: "function_name"
```

### Built-in Product Details Functions

#### simulate_product_details_mock

Rule-based generation using templates (default, no external dependencies).

```yaml
PRODUCT_DETAILS:
  FUNCTION: simulate_product_details_mock
```

Generates realistic mock data based on product category. No additional parameters required.

#### simulate_product_details_ollama

LLM-based generation using local Ollama for more realistic content.

```yaml
PRODUCT_DETAILS:
  FUNCTION: simulate_product_details_ollama
```

Requires Ollama running locally at `http://localhost:11434` with a compatible model.

### Complete Example

```yaml
STORAGE:
  PATH: "output/product_catalog"

RULE:
  CHARACTERISTICS:
    FUNCTION: simulate_characteristics_rule_based
    PARAMS:
      num_products: 50
      seed: 42

PRODUCT_DETAILS:
  FUNCTION: simulate_product_details_mock
```

### Usage

```python
from online_retail_simulator import simulate_characteristics, simulate_product_details, load_job_results

# Generate base products
job_info = simulate_characteristics("config.yaml")

# Add product details
job_info = simulate_product_details(job_info, "config.yaml")

# Load enriched products
results = load_job_results(job_info)
products_df = results["products"]
# products_df now includes: title, description, brand, features
```

## Configuration Validation

The config processor validates all configurations and provides clear error messages:

**Common Errors**:
- ❌ Including both `RULE` and `SYNTHESIZER` (choose one)
- ❌ Missing required parameters
- ❌ Typos in parameter names
- ❌ Invalid parameter types
- ❌ `training_data_path: null` for synthesizer mode

**Example Validation Error**:
```
ValueError: Unexpected parameters for RULE.METRICS.simulate_metrics_rule_based:
['SALE_PROB']. Expected: ['cart_to_order_rate', 'date_end', 'date_start',
'granularity', 'impression_to_visit_rate', 'sale_prob', 'seed', 'visit_to_cart_rate']
```

## Complete Configuration Examples

### Minimal Configuration

```yaml
RULE:
  CHARACTERISTICS:
    FUNCTION: simulate_characteristics_rule_based
    PARAMS:
      num_products: 20
  METRICS:
    FUNCTION: simulate_metrics_rule_based
    PARAMS:
      date_start: "2024-11-01"
      date_end: "2024-11-07"
      sale_prob: 0.8
```

### Production Configuration

```yaml
STORAGE:
  PATH: "output/production_sim"

RULE:
  CHARACTERISTICS:
    FUNCTION: simulate_characteristics_rule_based
    PARAMS:
      num_products: 1000
      seed: 42

  METRICS:
    FUNCTION: simulate_metrics_rule_based
    PARAMS:
      date_start: "2024-01-01"
      date_end: "2024-12-31"
      sale_prob: 0.65
      seed: 42
      granularity: "daily"
      impression_to_visit_rate: 0.18
      visit_to_cart_rate: 0.28
      cart_to_order_rate: 0.82
```

### Weekly Aggregation Configuration

```yaml
STORAGE:
  PATH: "output/weekly_metrics"

RULE:
  CHARACTERISTICS:
    FUNCTION: simulate_characteristics_rule_based
    PARAMS:
      num_products: 100
      seed: 42

  METRICS:
    FUNCTION: simulate_metrics_rule_based
    PARAMS:
      date_start: "2024-01-01"
      date_end: "2024-12-31"
      sale_prob: 0.7
      seed: 42
      granularity: "weekly"  # Weekly aggregation
```

## Custom Functions

You can register custom simulation and enrichment functions:

```python
from online_retail_simulator import register_metrics_function

def my_custom_metrics(product_characteristics, config):
    # Your custom implementation
    return sales_df

# Register it
register_metrics_function("my_custom_metrics", my_custom_metrics)
```

Then use in configuration:

```yaml
RULE:
  METRICS:
    FUNCTION: my_custom_metrics
    PARAMS:
      # Your custom parameters (no validation)
      my_param1: value1
      my_param2: value2
```

**Note**: Custom functions skip parameter validation since their schemas aren't known at config time.

## Next Steps

- **Examples**: See [User Guide](user-guide.md) for practical examples
- **API**: See [API Reference](api_reference.rst) for function documentation
- **Design**: See [Design Architecture](design.md) for system internals
