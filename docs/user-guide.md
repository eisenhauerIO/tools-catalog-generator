# User Guide

This guide provides comprehensive tutorials, use cases, and examples for the Online Retail Simulator.

## Getting Started

### Installation

Choose the installation option that best fits your needs:

```bash
# Basic installation (rule-based generation only)
pip install -e .

# With ML-based generation capabilities
pip install -e ".[synthesizer]"

# For development (includes testing and documentation tools)
pip install -e ".[dev]"
```

**System Requirements**:
- Python 3.8 or higher
- pip package manager

**Verifying Installation**:
```bash
# Run the demo to verify everything works
python demo/run_all_demos.py
```

### Your First Simulation

The simplest way to generate synthetic retail data:

```python
from online_retail_simulator import simulate, load_job_results

# Generate 30 days of sales data
job_info = simulate("demo/simulate/config_default_simulation.yaml")

# Load the results
products_df, sales_df = load_job_results(job_info)

# Explore the data
print(f"Generated {len(sales_df)} sales records")
print(f"Date range: {sales_df['date'].min()} to {sales_df['date'].max()}")
print(f"Categories: {sales_df['category'].unique()}")
print(f"Total revenue: ${sales_df['revenue'].sum():,.2f}")
```

### Understanding Output

The simulator generates realistic e-commerce data with two main structures:

#### Sales DataFrame (Primary Output)

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

#### Products DataFrame (Intermediate)

When using two-step generation:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `asin` | string | Unique product identifier | "BRPOIG8F1C" |
| `category` | string | Product category | "Electronics" |
| `price` | float | Unit price | 899.99 |

#### Working with the Data

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

## Who Should Use This?

### Data Scientist: ML Model Training

**Challenge**: "I need realistic e-commerce data for testing my models without using production data"

**Solution**:
```python
from online_retail_simulator import simulate, load_job_results

# Generate 30 days of sales data across 8 categories
job_info = simulate("config.yaml")
products_df, sales_df = load_job_results(job_info)
print(f"Generated {len(sales_df)} sales records for ML training")
```

**Why this matters**: Get diverse product catalogs with realistic pricing, daily sales patterns, and multiple categories - perfect for training recommendation engines, demand forecasting, or customer segmentation models.

**Benefits**:
- Privacy-safe synthetic data
- Configurable data volume and patterns
- Reproducible datasets with seed control
- Multiple product categories for diverse training scenarios

**Configuration Example**:
```yaml
SEED: 42
RULE:
  NUM_PRODUCTS: 1000
  DATE_START: "2024-01-01"
  DATE_END: "2024-12-31"
  SALE_PROB: 0.6
```

### Product Manager: A/B Test Simulation

**Challenge**: "I want to simulate A/B test results before launching catalog enrichment experiments"

**Solution**:
```python
from online_retail_simulator import simulate, enrich, load_job_results

# Generate baseline data
baseline_job = simulate("simulation_config.yaml")

# Simulate enrichment impact (30% of products, 50% boost, 7-day ramp)
enriched_job = enrich("enrichment_config.yaml", baseline_job)

# Load and compare results
_, baseline_df = load_job_results(baseline_job)
_, enriched_df = load_job_results(enriched_job)

lift = (enriched_df['revenue'].sum() / baseline_df['revenue'].sum() - 1) * 100
print(f"Projected revenue lift: {lift:.1f}%")
```

**Why this matters**: Test different enrichment strategies, effect sizes, and rollout timelines before committing resources to real experiments.

**Benefits**:
- Risk-free experiment planning
- Multiple scenario testing
- Statistical power analysis
- Resource allocation optimization

**Configuration Example**:
```yaml
SEED: 42
SYNTHESIZER:
  SYNTHESIZER_TYPE: gaussian_copula
  DEFAULT_PRODUCTS_ROWS: 500
  DEFAULT_SALES_ROWS: 10000
```

### Educator: Teaching Analytics Concepts

**Challenge**: "I need clean datasets to teach e-commerce analytics concepts to students"

**Solution**:
```bash
# Generate demo data for classroom use
python demo/run_all_demos.py

# Students get realistic data with:
# - Product catalogs (Electronics, Books, Clothing, etc.)
# - Daily sales transactions
# - Treatment effect examples
```

**Why this matters**: Provide students with realistic, privacy-safe data that demonstrates real-world e-commerce patterns and experimental design concepts.

**Benefits**:
- No privacy concerns with synthetic data
- Consistent datasets across semesters
- Real-world complexity without real-world complications
- Hands-on experience with experimental design

**Configuration Example**:
```yaml
SEED: 123
RULE:
  NUM_PRODUCTS: 50
  DATE_START: "2024-11-01"
  DATE_END: "2024-11-07"
  SALE_PROB: 0.8
```

### Developer: Application Testing

**Challenge**: "I need synthetic data to test my e-commerce application without production dependencies"

**Solution**:
```python
# Quick integration testing
from online_retail_simulator import simulate, load_job_results

# Generate test data matching your schema
job_info = simulate("test_config.yaml")
_, sales_df = load_job_results(job_info)

# Use in your tests
assert len(sales_df) > 0
assert all(sales_df['revenue'] == sales_df['price'] * sales_df['ordered_units'])
```

**Why this matters**: Eliminate dependencies on production databases, create reproducible test scenarios, and validate your application logic with consistent synthetic data.

**Benefits**:
- No production data dependencies
- Reproducible test scenarios
- Configurable edge cases
- Fast test execution

**Configuration Example**:
```yaml
SEED: 999
RULE:
  NUM_PRODUCTS: 10
  DATE_START: "2024-11-01"
  DATE_END: "2024-11-01"
  SALE_PROB: 1.0
```

### Advanced Use Cases

**Causal Inference Research**:
- Generate controlled datasets with known ground truth
- Test causal inference methodologies
- Validate statistical approaches before applying to real data

**Business Intelligence Development**:
- Develop and test dashboards
- Validate ETL pipelines
- Train stakeholders on new analytics tools

**Competitive Analysis Simulation**:
- Model competitor pricing strategies
- Simulate market response scenarios
- Test pricing optimization algorithms

**Compliance and Privacy Testing**:
- Test data anonymization techniques
- Validate privacy-preserving analytics
- Demonstrate compliance capabilities without exposing real data

## Tutorials

### Tutorial 1: Basic Simulation

Generate a basic dataset with rule-based simulation:

```python
from online_retail_simulator import simulate, load_job_results

# Generate 30 days of sales data
job_info = simulate("demo/simulate/config_default_simulation.yaml")

# Load the results
products_df, sales_df = load_job_results(job_info)

# Explore the data
print(f"Generated {len(sales_df)} sales records")
print(f"Date range: {sales_df['date'].min()} to {sales_df['date'].max()}")
print(f"Categories: {sales_df['category'].unique()}")
print(f"Total revenue: ${sales_df['revenue'].sum():,.2f}")
```

**Two-Step Generation** for more control:

```python
from online_retail_simulator import simulate_characteristics, simulate_metrics

# Step 1: Generate product catalog
products_df = simulate_characteristics("config.yaml")
print(f"Generated {len(products_df)} products")

# Step 2: Generate sales transactions
sales_df = simulate_metrics(products_df, "config.yaml")
print(f"Generated {len(sales_df)} sales records")
```

### Tutorial 2: Configuration Patterns

For complete configuration documentation, see the [Configuration Reference](configuration.md).

**Minimal Configuration**:
```yaml
# minimal_config.yaml
SEED: 42
STORAGE:
  PATH: "output"
RULE:
  NUM_PRODUCTS: 20
  DATE_START: "2024-11-01"
  DATE_END: "2024-11-07"
  SALE_PROB: 0.7
```

**Large Dataset Configuration**:
```yaml
# large_dataset_config.yaml
SEED: 42
STORAGE:
  PATH: "output"
RULE:
  NUM_PRODUCTS: 1000
  DATE_START: "2024-01-01"
  DATE_END: "2024-12-31"
  SALE_PROB: 0.6
```

**ML-Based Generation**:
```yaml
# ml_config.yaml
SEED: 42
STORAGE:
  PATH: "output"
SYNTHESIZER:
  SYNTHESIZER_TYPE: "gaussian_copula"
  DEFAULT_PRODUCTS_ROWS: 200
  DEFAULT_SALES_ROWS: 5000
```

### Tutorial 3: Enrichment Workflows

**Basic Enrichment**:

```python
from online_retail_simulator import simulate, enrich, load_job_results

# Generate baseline data
baseline_job = simulate("simulation_config.yaml")
_, baseline_df = load_job_results(baseline_job)
print(f"Baseline revenue: ${baseline_df['revenue'].sum():,.2f}")

# Apply enrichment
enriched_job = enrich("enrichment_config.yaml", baseline_job)
_, enriched_df = load_job_results(enriched_job)
print(f"Enriched revenue: ${enriched_df['revenue'].sum():,.2f}")

# Calculate lift
lift = (enriched_df['revenue'].sum() / baseline_df['revenue'].sum() - 1) * 100
print(f"Revenue lift: {lift:.1f}%")
```

**Enrichment Configuration**:
```yaml
# enrichment_config.yaml
IMPACT:
  FUNCTION: "combined_boost"
  PARAMS:
    effect_size: 0.3
    ramp_days: 5
    enrichment_fraction: 0.4
    enrichment_start: "2024-11-15"
    seed: 42
```

**Multiple Enrichment Scenarios**:

```python
from online_retail_simulator import simulate, enrich, load_job_results
import yaml
from pathlib import Path

# Generate baseline once
baseline_job = simulate("simulation_config.yaml")
_, baseline_df = load_job_results(baseline_job)
baseline_revenue = baseline_df['revenue'].sum()

# Test multiple scenarios
scenarios = [
    {"effect_size": 0.1, "enrichment_fraction": 0.2},  # Conservative
    {"effect_size": 0.3, "enrichment_fraction": 0.3},  # Moderate
    {"effect_size": 0.5, "enrichment_fraction": 0.4},  # Aggressive
]

results = []
for i, params in enumerate(scenarios):
    # Create temporary config file for this scenario
    config = {
        "IMPACT": {
            "FUNCTION": "combined_boost",
            "PARAMS": {
                **params,
                "ramp_days": 7,
                "enrichment_start": "2024-11-15",
                "seed": 42
            }
        }
    }

    config_path = f"temp_scenario_{i}.yaml"
    with open(config_path, 'w') as f:
        yaml.dump(config, f)

    # Apply enrichment
    enriched_job = enrich(config_path, baseline_job)
    _, enriched_df = load_job_results(enriched_job)
    lift = (enriched_df['revenue'].sum() / baseline_revenue - 1) * 100

    results.append({
        "scenario": f"Scenario {i+1}",
        "effect_size": params["effect_size"],
        "enrichment_fraction": params["enrichment_fraction"],
        "revenue_lift": lift
    })

    # Clean up temp file
    Path(config_path).unlink()

# Display results
for result in results:
    print(f"{result['scenario']}: {result['revenue_lift']:.1f}% lift")
```

### Tutorial 4: A/B Testing

**Complete A/B Test Simulation**:

```python
from online_retail_simulator import simulate, enrich, load_job_results
import pandas as pd

def run_ab_test(simulation_config, enrichment_config, test_name):
    """Run a complete A/B test simulation"""

    # Generate control group (baseline)
    control_job = simulate(simulation_config)
    _, control_df = load_job_results(control_job)
    control_revenue = control_df['revenue'].sum()

    # Generate treatment group (enriched)
    treatment_job = enrich(enrichment_config, control_job)
    _, treatment_df = load_job_results(treatment_job)
    treatment_revenue = treatment_df['revenue'].sum()

    # Calculate metrics
    lift = (treatment_revenue / control_revenue - 1) * 100

    results = {
        'test_name': test_name,
        'control_revenue': control_revenue,
        'treatment_revenue': treatment_revenue,
        'absolute_lift': treatment_revenue - control_revenue,
        'relative_lift_pct': lift,
        'control_transactions': len(control_df),
        'treatment_transactions': len(treatment_df)
    }

    return results

# Run multiple tests
tests = [
    {
        'name': 'Conservative Test',
        'enrichment': {
            'IMPACT': {
                'FUNCTION': 'combined_boost',
                'PARAMS': {
                    'effect_size': 0.2,
                    'enrichment_fraction': 0.2,
                    'ramp_days': 3,
                    'enrichment_start': '2024-11-15',
                    'seed': 42
                }
            }
        }
    },
    {
        'name': 'Aggressive Test',
        'enrichment': {
            'IMPACT': {
                'FUNCTION': 'combined_boost',
                'PARAMS': {
                    'effect_size': 0.6,
                    'enrichment_fraction': 0.5,
                    'ramp_days': 7,
                    'enrichment_start': '2024-11-10',
                    'seed': 42
                }
            }
        }
    }
]

# Run all tests
simulation_config = "demo/simulate/config_default_simulation.yaml"
all_results = []

for test in tests:
    result = run_ab_test(simulation_config, test['enrichment'], test['name'])
    all_results.append(result)

# Display results
results_df = pd.DataFrame(all_results)
print("A/B Test Results:")
print(results_df[['test_name', 'relative_lift_pct', 'absolute_lift']])
```

### Tutorial 5: Analysis & Visualization

**Category Analysis**:

```python
from online_retail_simulator import simulate, load_job_results
import pandas as pd
import matplotlib.pyplot as plt

# Generate data
job_info = simulate("config.yaml")
_, sales_df = load_job_results(job_info)

# Revenue by category
category_revenue = sales_df.groupby('category')['revenue'].sum().sort_values(ascending=False)
print("Revenue by Category:")
print(category_revenue)

# Plot category performance
category_revenue.plot(kind='bar', title='Revenue by Category')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

**Time Series Analysis**:

```python
# Daily sales trends
daily_sales = sales_df.groupby('date').agg({
    'ordered_units': 'sum',
    'revenue': 'sum'
}).reset_index()

daily_sales['date'] = pd.to_datetime(daily_sales['date'])

# Plot daily trends
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

ax1.plot(daily_sales['date'], daily_sales['ordered_units'])
ax1.set_title('Daily Quantity Sold')
ax1.set_ylabel('Quantity')

ax2.plot(daily_sales['date'], daily_sales['revenue'])
ax2.set_title('Daily Revenue')
ax2.set_ylabel('Revenue ($)')

plt.tight_layout()
plt.show()
```

**Product Performance Analysis**:

```python
# Top performing products
product_performance = sales_df.groupby(['asin', 'category']).agg({
    'ordered_units': 'sum',
    'revenue': 'sum',
    'price': 'first'
}).reset_index()

# Top 10 products by revenue
top_products = product_performance.nlargest(10, 'revenue')
print("Top 10 Products by Revenue:")
print(top_products[['asin', 'category', 'revenue']])

# Revenue per unit analysis
product_performance['revenue_per_unit'] = product_performance['revenue'] / product_performance['ordered_units']
top_efficiency = product_performance.nlargest(10, 'revenue_per_unit')
print("\nMost Efficient Products (Revenue per Unit):")
print(top_efficiency[['asin', 'category', 'revenue_per_unit']])
```

## Integration Guides

### Jupyter Notebook Integration

```python
# Cell 1: Setup
%matplotlib inline
import pandas as pd
import matplotlib.pyplot as plt
from online_retail_simulator import simulate, enrich, load_job_results

# Cell 2: Generate data
job_info = simulate("config.yaml")
_, sales_df = load_job_results(job_info)
print(f"Generated {len(sales_df)} records")
sales_df.head()

# Cell 3: Quick visualization
sales_df.groupby('category')['revenue'].sum().plot(kind='bar')
plt.title('Revenue by Category')
plt.show()

# Cell 4: Time series
daily_revenue = sales_df.groupby('date')['revenue'].sum()
daily_revenue.plot(title='Daily Revenue Trend')
plt.show()
```

### Pandas Integration

```python
from online_retail_simulator import simulate, load_job_results

# Seamless pandas integration
job_info = simulate("config.yaml")
_, sales_df = load_job_results(job_info)

# Standard pandas operations work immediately
summary_stats = sales_df.describe()
category_pivot = sales_df.pivot_table(
    values='revenue',
    index='date',
    columns='category',
    aggfunc='sum'
)

# Export to various formats
sales_df.to_csv('sales_data.csv', index=False)
sales_df.to_parquet('sales_data.parquet')
sales_df.to_json('sales_data.json', orient='records')
```

## Next Steps

- **Configuration Details**: See the [Configuration Reference](configuration.md) for all available parameters
- **API Documentation**: Explore the [API Reference](api_reference.rst) for detailed function documentation
- **Architecture**: Learn about the system design in the [Design Documentation](design.md)
