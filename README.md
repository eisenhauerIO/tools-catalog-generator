# Online Retail Simulator

Generate synthetic retail data for testing, demos, and experimentation without exposing real business data.

## Quick Start

```bash
# Install
pip install -e .

# Run demo
python demo/run_all_demos.py

# Generate data
python -c "from online_retail_simulator import simulate; \
    df = simulate('demo/simulate/config_default_simulation.yaml'); \
    print(f'Generated {len(df)} sales records')"
```

## Who Should Use This?

- **Data Scientists**: Generate realistic e-commerce data for ML model training without production data
- **Product Managers**: Simulate A/B test results before launching catalog enrichment experiments
- **Educators**: Create clean datasets to teach e-commerce analytics concepts to students
- **Developers**: Generate synthetic data to test applications without production dependencies

[See complete user stories and use cases →](https://eisenhauerio.github.io/tools-catalog-generator/user-guide.html#who-should-use-this)

## Key Features

- **Flexible Generation**: Rule-based patterns or ML-based synthesis (requires SDV)
- **A/B Testing Simulation**: Compare baseline vs enriched scenarios with realistic treatment effects
- **Realistic Data**: 8 product categories with appropriate pricing, daily sales cycles, and funnel metrics
- **Reproducible**: Seed-controlled deterministic generation
- **Developer-Friendly**: Pandas DataFrames, YAML configuration, Python 3.8+ compatibility

## Documentation

📚 **[Complete Documentation](https://eisenhauerio.github.io/tools-catalog-generator/)**

- **[User Guide](https://eisenhauerio.github.io/tools-catalog-generator/user-guide.html)** - Tutorials, use cases, and practical examples
- **[Configuration Reference](https://eisenhauerio.github.io/tools-catalog-generator/configuration.html)** - All parameters and options
- **[API Reference](https://eisenhauerio.github.io/tools-catalog-generator/api_reference.html)** - Detailed function documentation
- **[Design Architecture](https://eisenhauerio.github.io/tools-catalog-generator/design.html)** - System design and technical details

## Example Usage

```python
from online_retail_simulator import simulate, enrich, load_job_results

# Generate baseline sales data
baseline_job = simulate("config.yaml")

# Simulate enrichment impact
enriched_job = enrich("enrichment_config.yaml", baseline_job)

# Load and compare results
_, baseline_df = load_job_results(baseline_job)
_, enriched_df = load_job_results(enriched_job)

lift = (enriched_df['revenue'].sum() / baseline_df['revenue'].sum() - 1) * 100
print(f"Projected revenue lift: {lift:.1f}%")
```

For more examples, see the [User Guide](https://eisenhauerio.github.io/tools-catalog-generator/user-guide.html).

## Getting Help

- **[User Guide](https://eisenhauerio.github.io/tools-catalog-generator/user-guide.html)** - Start here for tutorials and examples
- **[GitHub Issues](https://github.com/eisenhauerio/tools-catalog-generator/issues)** - Report bugs or request features
- **[Configuration Guide](https://eisenhauerio.github.io/tools-catalog-generator/configuration.html)** - Complete parameter reference
