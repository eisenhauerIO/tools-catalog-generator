# Configuration Guide

The Online Retail Simulator uses YAML configuration files to control all aspects of data generation and enrichment. This guide covers the complete configuration schema and common patterns.

## Configuration Structure

All configuration files follow a hierarchical YAML structure with these main sections:

```yaml
SEED: 42                    # Global reproducibility control

OUTPUT:                     # Output file settings
  DIR: "output"
  FILE_PREFIX: "experiment"

RULE:                       # Rule-based generation settings
  # Rule-specific parameters

SYNTHESIZER:                # ML-based generation settings
  # Synthesizer-specific parameters

IMPACT:                     # Enrichment settings
  # Treatment effect parameters
```

## Global Settings

### SEED
Controls reproducibility across all random operations.

```yaml
SEED: 42  # Any integer value
```

**Usage**:
- Use the same seed for reproducible results
- Change seed to generate different datasets
- Required for scientific reproducibility

### OUTPUT
Controls where and how files are saved.

```yaml
OUTPUT:
  DIR: "output"              # Output directory path
  FILE_PREFIX: "my_experiment"  # Prefix for all output files
```

**Generated files**:
- `{PREFIX}_products.json` - Product catalog
- `{PREFIX}_sales.json` - Sales transactions
- `{PREFIX}_enriched.json` - Enriched sales data

## Rule-Based Configuration

Rule-based mode generates data using deterministic algorithms with configurable parameters.

### Basic Parameters

```yaml
RULE:
  NUM_PRODUCTS: 100           # Total number of products to generate
  DATE_START: "2024-11-01"    # Start date (YYYY-MM-DD)
  DATE_END: "2024-11-30"      # End date (YYYY-MM-DD)
  SALE_PROB: 0.7              # Daily probability of sale per product (0.0-1.0)
  GRANULARITY: "daily"        # Time granularity: "daily" or "weekly" (default: "daily")
```

#### Granularity Parameter

The `GRANULARITY` parameter controls the time granularity of the generated metrics data.

**Options:**
- `"daily"` (default): One row per product per day
- `"weekly"`: One row per product per week (ISO week, Monday-Sunday)

**Weekly Granularity Behavior:**

When set to `"weekly"`:
1. **Date range adjustment**: The date range is automatically expanded to full week boundaries
   - `DATE_START` is moved back to the Monday of that week
   - `DATE_END` is moved forward to the Sunday of that week
   - Example: `2024-01-03` to `2024-01-25` becomes `2024-01-01` (Monday) to `2024-01-28` (Sunday)

2. **Data aggregation**:
   - All funnel metrics (`impressions`, `visits`, `cart_adds`, `ordered_units`, `revenue`) are summed across the week
   - `average_selling_price` is recalculated as `revenue / ordered_units` for the week
   - `date` column shows the Monday of each week (YYYY-MM-DD format)
   - All products appear for all weeks, including weeks with zero activity

3. **ISO week standard**: Weeks run from Monday to Sunday

**Example - Daily (default):**
```yaml
RULE:
  METRICS:
    FUNCTION: simulate_metrics_rule_based
    PARAMS:
      date_start: "2024-01-01"
      date_end: "2024-01-31"
      sale_prob: 0.7
      granularity: "daily"  # 310 rows (10 products × 31 days)
```

**Example - Weekly:**
```yaml
RULE:
  METRICS:
    FUNCTION: simulate_metrics_rule_based
    PARAMS:
      date_start: "2024-01-01"
      date_end: "2024-01-31"
      sale_prob: 0.7
      granularity: "weekly"  # 50 rows (10 products × 5 weeks)
```

### Advanced Parameters

```yaml
RULE:
  NUM_PRODUCTS: 100
  DATE_START: "2024-11-01"
  DATE_END: "2024-11-30"
  SALE_PROB: 0.7

  # Category distribution (optional)
  CATEGORY_WEIGHTS:
    Electronics: 0.2
    Books: 0.15
    Clothing: 0.15
    "Home & Garden": 0.15
    Sports: 0.1
    Beauty: 0.1
    Toys: 0.1
    Automotive: 0.05

  # Price ranges by category (optional)
  PRICE_RANGES:
    Electronics: [50, 2000]
    Books: [10, 100]
    Clothing: [20, 300]
```

### Parameter Validation

- `NUM_PRODUCTS`: Must be positive integer
- `DATE_START`/`DATE_END`: Must be valid dates in YYYY-MM-DD format
- `SALE_PROB`: Must be between 0.0 and 1.0
- `CATEGORY_WEIGHTS`: Must sum to 1.0 if provided

## Synthesizer Configuration

Synthesizer mode uses machine learning models to generate more sophisticated patterns.

### Basic Configuration

```yaml
SYNTHESIZER:
  SYNTHESIZER_TYPE: "gaussian_copula"    # SDV synthesizer type
  DEFAULT_PRODUCTS_ROWS: 50              # Number of products to generate
  DEFAULT_SALES_ROWS: 1000               # Number of sales records to generate
```

### Supported Synthesizer Types

| Type | Description | Use Case |
|------|-------------|----------|
| `gaussian_copula` | Gaussian copula model | General purpose, good balance |
| `ctgan` | Conditional GAN | Complex patterns, longer training |
| `tvae` | Variational autoencoder | Tabular data, fast training |
| `copula_gan` | Copula + GAN hybrid | High quality, moderate speed |

### Advanced Configuration

```yaml
SYNTHESIZER:
  SYNTHESIZER_TYPE: "gaussian_copula"
  DEFAULT_PRODUCTS_ROWS: 50
  DEFAULT_SALES_ROWS: 1000

  # Model training parameters
  EPOCHS: 300                 # Training epochs for neural models
  BATCH_SIZE: 500            # Batch size for training

  # Quality vs speed tradeoff
  ENFORCE_MIN_MAX_VALUES: true    # Enforce realistic value ranges
  ENFORCE_ROUNDING: true          # Round to appropriate precision
```

## Enrichment Configuration

Enrichment applies treatment effects to simulate A/B testing scenarios.

### Basic Impact Configuration

```yaml
IMPACT:
  FUNCTION: "combined_boost"     # Impact function name
  PARAMS:                        # Function-specific parameters
    effect_size: 0.5            # 50% improvement
    ramp_days: 7                # Gradual rollout over 7 days
    enrichment_fraction: 0.3    # 30% of products get enriched
    enrichment_start: "2024-11-15"  # When enrichment begins
    seed: 42                    # Reproducibility for treatment assignment
```

### Available Impact Functions

#### quantity_boost
Simple multiplicative increase in sale quantities.

```yaml
IMPACT:
  FUNCTION: "quantity_boost"
  PARAMS:
    effect_size: 0.3           # 30% increase in quantities
```

#### probability_boost
Increases the probability of sales occurring.

```yaml
IMPACT:
  FUNCTION: "probability_boost"
  PARAMS:
    effect_size: 0.2           # 20% increase in sale probability
```

#### combined_boost (Recommended)
Realistic gradual rollout with partial treatment.

```yaml
IMPACT:
  FUNCTION: "combined_boost"
  PARAMS:
    effect_size: 0.5           # 50% improvement when fully ramped
    ramp_days: 7               # Linear ramp over 7 days
    enrichment_fraction: 0.3   # 30% of products treated
    enrichment_start: "2024-11-15"  # Start date for treatment
    seed: 42                   # Seed for treatment assignment
```

## Configuration Examples

### Quick Testing
Minimal configuration for rapid iteration:

```yaml
SEED: 42
OUTPUT:
  DIR: "test_output"
  FILE_PREFIX: "quick_test"
RULE:
  NUM_PRODUCTS: 10
  DATE_START: "2024-11-01"
  DATE_END: "2024-11-03"
  SALE_PROB: 1.0
```

### Educational Demo
Balanced dataset for teaching:

```yaml
SEED: 123
OUTPUT:
  DIR: "demo_output"
  FILE_PREFIX: "classroom_demo"
RULE:
  NUM_PRODUCTS: 50
  DATE_START: "2024-11-01"
  DATE_END: "2024-11-07"
  SALE_PROB: 0.8
```

### Research Experiment
Large-scale synthetic data generation:

```yaml
SEED: 42
OUTPUT:
  DIR: "research_output"
  FILE_PREFIX: "experiment_001"
SYNTHESIZER:
  SYNTHESIZER_TYPE: "gaussian_copula"
  DEFAULT_PRODUCTS_ROWS: 500
  DEFAULT_SALES_ROWS: 10000
```

### A/B Test Simulation
Complete enrichment workflow:

```yaml
# Simulation config
SEED: 42
OUTPUT:
  DIR: "ab_test_output"
  FILE_PREFIX: "baseline"
RULE:
  NUM_PRODUCTS: 200
  DATE_START: "2024-11-01"
  DATE_END: "2024-11-30"
  SALE_PROB: 0.6

---
# Enrichment config (separate file)
IMPACT:
  FUNCTION: "combined_boost"
  PARAMS:
    effect_size: 0.4
    ramp_days: 5
    enrichment_fraction: 0.25
    enrichment_start: "2024-11-15"
    seed: 42
```

## Configuration Validation

The system validates configurations at runtime and provides helpful error messages:

### Common Validation Errors

```yaml
# ERROR: Invalid date format
DATE_START: "11/01/2024"  # Should be "2024-11-01"

# ERROR: Probability out of range
SALE_PROB: 1.5            # Should be 0.0-1.0

# ERROR: Missing required field
RULE:
  NUM_PRODUCTS: 100
  # Missing DATE_START and DATE_END

# ERROR: Invalid synthesizer type
SYNTHESIZER:
  SYNTHESIZER_TYPE: "invalid_type"  # Should be supported type
```

### Validation Messages
The system provides clear feedback:

```
ConfigurationError: DATE_START must be in YYYY-MM-DD format, got '11/01/2024'
ConfigurationError: SALE_PROB must be between 0.0 and 1.0, got 1.5
ConfigurationError: Missing required field 'DATE_START' in RULE section
```

## Best Practices

### Reproducibility
Always set a seed for reproducible results:

```yaml
SEED: 42  # Use consistent seed across experiments
```

### File Organization
Use descriptive prefixes and organized directories:

```yaml
OUTPUT:
  DIR: "experiments/2024-11/baseline"
  FILE_PREFIX: "exp_001_baseline"
```

### Parameter Tuning
Start with conservative parameters and iterate:

```yaml
# Start conservative
RULE:
  NUM_PRODUCTS: 50      # Small for testing
  SALE_PROB: 0.5        # Moderate probability

# Scale up after validation
RULE:
  NUM_PRODUCTS: 500     # Production scale
  SALE_PROB: 0.7        # Tuned probability
```

### Enrichment Testing
Test enrichment effects with known parameters:

```yaml
IMPACT:
  FUNCTION: "quantity_boost"
  PARAMS:
    effect_size: 0.1    # Small, measurable effect for validation
```

## Configuration Inheritance

The system supports configuration inheritance through defaults:

1. **Built-in defaults** (config_defaults.yaml)
2. **User configuration** (your YAML file)
3. **Runtime overrides** (programmatic changes)

Later configurations override earlier ones, allowing flexible customization while maintaining sensible defaults.
