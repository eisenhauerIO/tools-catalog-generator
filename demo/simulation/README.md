# Simulation Examples

This directory contains examples demonstrating the core simulation capabilities of the Online Retail Simulator.

## Files

### Main Examples
- `example.py` - Basic simulation demo using rule-based generation
- `example_enrichment.py` - Complete workflow showing simulation + enrichment

### Configuration Files
- `config_rule.yaml` - Rule-based simulation configuration
- `config_synthesizer.yaml` - ML-based simulation configuration (requires SDV)
- `config_simulation.yaml` - General simulation parameters
- `config_enrichment.yaml` - Enrichment treatment configuration

## Running Examples

### Basic Simulation
```bash
cd demo/simulation
python example.py
```

This demonstrates:
- Generating synthetic product catalogs
- Creating realistic sales transactions
- Exporting data to JSON format

### Simulation with Enrichment
```bash
cd demo/simulation
python example_enrichment.py
```

This shows the complete workflow:
- Generate baseline sales data
- Apply enrichment treatments
- Compare factual vs counterfactual outcomes

## Configuration Modes

### Rule-Based Mode
Uses simple statistical rules to generate data:
- Fast and lightweight
- No external ML dependencies
- Good for testing and demos

### Synthesizer Mode
Uses machine learning models (SDV) for generation:
- More realistic data patterns
- Requires `pip install -e ".[synthesizer]"`
- Better for research applications

## Output Files

Generated files are saved to `demo/demo/output/` with configurable prefixes:
- `*_products.json` - Product catalog
- `*_sales.json` - Sales transactions
- `*_enriched.json` - Enriched sales data
- `*_factual.json` - Factual outcomes
- `*_counterfactual.json` - Counterfactual outcomes
