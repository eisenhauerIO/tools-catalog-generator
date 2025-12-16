# Demo Directory

This directory contains examples and demonstrations for the Online Retail Simulator.

## Structure

### `simulation/`
Core simulation examples showing how to generate synthetic retail data:
- Basic product catalog and sales generation
- Rule-based vs ML-based simulation modes
- Configuration examples and workflows

### `enrichment/`
Enrichment examples showing how to apply treatments and register custom functions:
- Custom enrichment effect functions
- Function registration system
- Treatment configuration examples

### Legacy Files (Root Level)
- `config_*.yaml` - Original configuration files (kept for backward compatibility)
- `example*.py` - Original example scripts (kept for backward compatibility)

## Quick Start

### Generate Basic Sales Data
```bash
cd demo/simulation
python example.py
```

### Try Custom Enrichment Functions
```bash
cd demo/enrichment
python registration_example.py
```

## Configuration Files

The simulator uses YAML configuration files to control behavior:
- **Simulation configs**: Control data generation parameters
- **Enrichment configs**: Define treatment effects and parameters

See the README files in each subdirectory for detailed usage instructions.
