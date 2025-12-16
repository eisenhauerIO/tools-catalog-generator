# Project Structure

## Root Directory
- `pyproject.toml` - Package configuration and dependencies
- `README.md` - Main documentation and usage examples
- `NEXT.md` - Development roadmap and next actions

## Core Package (`online_retail_simulator/`)
- `__init__.py` - Package entry point, exports main functions
- `simulate.py` - Main workflow orchestrator
- `config_defaults.yaml` - Default configuration values
- `config_processor.py` - Configuration handling utilities

### Simulation Modules
- `simulate_characteristics.py` - Product catalog generation
- `simulate_characteristics_rule_based.py` - Rule-based product generation
- `simulate_characteristics_synthesizer_based.py` - ML-based product generation
- `simulate_metrics.py` - Sales transaction generation
- `simulate_metrics_rule_based.py` - Rule-based sales generation
- `simulate_metrics_synthesizer_based.py` - ML-based sales generation

### Enrichment System
- `enrichment_application.py` - Apply enrichment transformations
- `enrichment_impact_library.py` - Library of impact functions

## Testing (`online_retail_simulator/tests/`)
- `test_*.py` - Unit tests for each module
- `config_*.yaml` - Test configuration files
- `df_start.pkl` - Test data fixtures
- `import_helpers.py` - Test utilities

## Demo & Examples (`demo/`)
- `example.py` - Main demonstration script
- `config_rule.yaml` - Rule-based simulation config
- `config_synthesizer.yaml` - Synthesizer-based simulation config
- `demo/output/` - Generated demo files

## Development Support
- `debug/` - Development notebooks and debugging tools
- `workflows/` - Documentation for validation workflows
- `_support/` - External support materials and submodules

## Configuration Patterns
- YAML-based configuration with hierarchical structure
- Mode-specific sections: `RULE`, `SYNTHESIZER`, `BASELINE`
- Output control via `OUTPUT.dir` and `OUTPUT.file_prefix`
- Reproducibility via `SEED` parameter

## File Naming Conventions
- Rule-based outputs: `<prefix>_products.json`, `<prefix>_sales.json`
- Synthesizer outputs: `<prefix>_model_*.pkl`, `<prefix>_mc_*.json`
- Enrichment outputs: `<prefix>_enriched.json`, `<prefix>_factual.json`, `<prefix>_counterfactual.json`
