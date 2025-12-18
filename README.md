# Online Retail Simulator

Generate synthetic retail data for testing, demos, and experimentation without exposing real business data.

## User Stories

### 📊 As a Data Scientist
**"I need realistic e-commerce data for testing my models without using production data"**

```python
from online_retail_simulator import simulate

# Generate 30 days of sales data across 8 categories
sales_df = simulate("config.yaml")
print(f"Generated {len(sales_df)} sales records for ML training")
```

**Why this matters:** Get diverse product catalogs with realistic pricing, daily sales patterns, and multiple categories - perfect for training recommendation engines, demand forecasting, or customer segmentation models.

### 🧪 As a Product Manager
**"I want to simulate A/B test results before launching catalog enrichment experiments"**

```python
from online_retail_simulator import simulate, enrich

# Generate baseline data
baseline_df = simulate("simulation_config.yaml")

# Simulate enrichment impact (30% of products, 50% boost, 7-day ramp)
enriched_df = enrich("enrichment_config.yaml", baseline_df)

# Compare results
lift = (enriched_df['revenue'].sum() / baseline_df['revenue'].sum() - 1) * 100
print(f"Projected revenue lift: {lift:.1f}%")
```

**Why this matters:** Test different enrichment strategies, effect sizes, and rollout timelines before committing resources to real experiments.

### 🎓 As an Educator
**"I need clean datasets to teach e-commerce analytics concepts to students"**

```bash
# Generate demo data for classroom use
python demo/run_all_demos.py

# Students get realistic data with:
# - Product catalogs (Electronics, Books, Clothing, etc.)
# - Daily sales transactions
# - Treatment effect examples
```

**Why this matters:** Provide students with realistic, privacy-safe data that demonstrates real-world e-commerce patterns and experimental design concepts.

### 🔧 As a Developer
**"I need synthetic data to test my e-commerce application without production dependencies"**

```python
# Quick integration testing
from online_retail_simulator import simulate

# Generate test data matching your schema
sales_df = simulate("test_config.yaml")

# Use in your tests
assert len(sales_df) > 0
assert all(sales_df['revenue'] == sales_df['price'] * sales_df['ordered_units'])
```

**Why this matters:** Eliminate dependencies on production databases, create reproducible test scenarios, and validate your application logic with consistent synthetic data.

## Quick Start

### 1. Install
```bash
# Basic installation (rule-based generation)
pip install -e .

# With ML-based generation (optional)
pip install -e ".[synthesizer]"

# For development
pip install -e ".[dev]"
```

### 2. Run Demo
```bash
python demo/run_all_demos.py
```

### 3. Basic Usage
```python
from online_retail_simulator import simulate

# Generate data using config file
sales_df = simulate("demo/simulate/config_default_simulation.yaml")
print(f"Generated {len(sales_df)} sales records")
```

## Configuration Examples

### Simple Rule-Based Generation
Perfect for getting started or when you need predictable patterns:

```yaml
SEED: 42

OUTPUT:
  DIR: output
  FILE_PREFIX: my_experiment

RULE:
  NUM_PRODUCTS: 50
  DATE_START: "2024-11-01"
  DATE_END: "2024-11-30"
  SALE_PROB: 0.7
  GRANULARITY: "daily"  # or "weekly" for aggregated data
```

### ML-Based Generation (Advanced)
For more sophisticated, learned patterns from real data:

```yaml
SEED: 42

OUTPUT:
  DIR: output
  FILE_PREFIX: my_experiment

SYNTHESIZER:
  SYNTHESIZER_TYPE: gaussian_copula
  DEFAULT_PRODUCTS_ROWS: 30
  DEFAULT_SALES_ROWS: 5000
```

### Enrichment Configuration
Simulate catalog improvements and their business impact:

```yaml
IMPACT:
  FUNCTION: "combined_boost"
  PARAMS:
    effect_size: 0.5        # 50% improvement
    ramp_days: 7            # Gradual rollout over 7 days
    enrichment_fraction: 0.3 # 30% of products get enriched
    enrichment_start: "2024-11-15"
    seed: 42
```

## API Usage Patterns

### One-Step Generation (Recommended)
```python
from online_retail_simulator import simulate

# Generate complete sales dataset
sales_df = simulate("config.yaml")
```

### Two-Step Generation (Advanced Control)
```python
from online_retail_simulator import simulate_characteristics, simulate_metrics

# Step 1: Generate product catalog
products_df = simulate_characteristics("config.yaml")

# Step 2: Generate sales transactions
sales_df = simulate_metrics(products_df, "config.yaml")
```

### Enrichment Workflow
```python
from online_retail_simulator import simulate, enrich

# Generate baseline data
baseline_df = simulate("simulation_config.yaml")

# Apply treatment effects
enriched_df = enrich("enrichment_config.yaml", baseline_df)
```
## Enrichment & Treatment Effects

### The Business Problem
**"How do I know if improving my product catalog will actually increase sales?"**

Traditional A/B testing requires:
- Real traffic and revenue at risk
- Weeks or months to get statistical significance
- Complex experimental design and analysis

### The Simulation Solution
Test your enrichment strategies with synthetic data first:

```python
from online_retail_simulator import simulate, enrich

# Generate realistic baseline sales
baseline_df = simulate("simulation_config.yaml")

# Simulate different enrichment scenarios
scenarios = [
    {"effect_size": 0.2, "enrichment_fraction": 0.1},  # Conservative
    {"effect_size": 0.5, "enrichment_fraction": 0.3},  # Moderate
    {"effect_size": 0.8, "enrichment_fraction": 0.5},  # Aggressive
]

for scenario in scenarios:
    enriched_df = enrich(scenario, baseline_df)
    lift = calculate_lift(baseline_df, enriched_df)
    print(f"Scenario {scenario}: {lift:.1f}% revenue lift")
```

### Built-in Impact Functions

| Function | Use Case | Parameters |
|----------|----------|------------|
| `quantity_boost` | Simple volume increase | `effect_size` |
| `probability_boost` | Improved conversion | `effect_size` |
| `combined_boost` | Realistic gradual rollout | `effect_size`, `ramp_days`, `enrichment_fraction` |

### Realistic Experimental Design
- **Gradual rollout**: Effects ramp up over configurable days
- **Partial treatment**: Only a fraction of products get enriched
- **Date-based activation**: Effects start on specific dates
- **Reproducible**: Seed-controlled for consistent results

### Try It Yourself
```bash
python demo/enrich/run_default_enrichment.py
```

## Documentation

📚 **[Full Documentation](https://eisenhauerio.github.io/tools-catalog-generator/)** - Complete guides, API reference, and examples

- **[Use Cases](https://eisenhauerio.github.io/tools-catalog-generator/use_cases.html)** - Real-world scenarios and user stories
- **[Design Architecture](https://eisenhauerio.github.io/tools-catalog-generator/design.html)** - System design and technical details
- **[Configuration Guide](https://eisenhauerio.github.io/tools-catalog-generator/configuration.html)** - Complete configuration reference
- **[API Reference](https://eisenhauerio.github.io/tools-catalog-generator/api_reference.html)** - Detailed API documentation
- **[Examples](https://eisenhauerio.github.io/tools-catalog-generator/examples.html)** - Code examples and tutorials

## Key Capabilities

### 🎯 **Flexible Generation Modes**
- **Rule-based**: Simple, predictable patterns for testing and education
- **ML-based**: Sophisticated patterns learned from real data (requires SDV)
- **Hybrid**: Combine both approaches for different use cases

### 🧪 **Experiment Simulation**
- **A/B testing**: Compare baseline vs enriched scenarios
- **Treatment effects**: Gradual rollouts, partial coverage, date-based activation
- **Custom functions**: Register your own enrichment impact functions

### 📊 **Realistic Data Patterns**
- **8 product categories**: Electronics, Books, Clothing, Home & Garden, Sports, Beauty, Toys, Automotive
- **Daily sales cycles**: Configurable probability patterns
- **Price distributions**: Category-appropriate pricing ranges
- **Revenue calculations**: Automatic quantity × price calculations

### 🔧 **Developer-Friendly**
- **Pandas integration**: Native DataFrame output
- **Configuration-driven**: YAML-based workflow control
- **Reproducible**: Seed-controlled deterministic generation
- **Python 3.8+**: Broad compatibility with modern environments

## Data Schema

### Sales DataFrame (Primary Output)
The main output contains everything you need for analysis with customer journey funnel metrics:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `asin` | string | Unique product identifier | "BRPOIG8F1C" |
| `category` | string | Product category | "Electronics" |
| `price` | float | Unit price | 899.99 |
| `date` | string | Sale date (YYYY-MM-DD) or week start for weekly granularity | "2024-11-15" |
| `impressions` | int | Number of product impressions | 50 |
| `visits` | int | Number of product page visits | 10 |
| `cart_adds` | int | Number of add-to-cart actions | 3 |
| `ordered_units` | int | Units sold/ordered | 2 |
| `revenue` | float | Total revenue (price × ordered_units) | 1799.98 |
| `average_selling_price` | float | Effective selling price per unit | 899.99 |

### Products DataFrame (Intermediate)
When using two-step generation:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `asin` | string | Unique product identifier | "BRPOIG8F1C" |
| `category` | string | Product category | "Electronics" |
| `price` | float | Unit price | 899.99 |

### Usage Examples
```python
# Analyze by category
category_revenue = sales_df.groupby('category')['revenue'].sum()

# Daily trends
daily_sales = sales_df.groupby('date')['ordered_units'].sum()

# Product performance
top_products = sales_df.groupby('asin')['revenue'].sum().sort_values(ascending=False)

# Funnel conversion analysis
conversion_rate = sales_df['ordered_units'].sum() / sales_df['impressions'].sum()
cart_conversion = sales_df['cart_adds'].sum() / sales_df['visits'].sum()
```
