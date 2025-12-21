# Design Architecture

The Online Retail Simulator follows a modular, configuration-driven architecture that supports multiple generation modes and extensible enrichment capabilities.

## Core Design Principles

### 1. Configuration-Driven Workflow
All simulation behavior is controlled through YAML configuration files, enabling:
- Reproducible experiments with version-controlled configs
- Easy parameter sweeps and scenario testing
- Clear separation of logic and parameters

### 2. Modular Architecture
The system is organized into distinct, loosely-coupled modules:
- **Core**: Shared infrastructure including `FunctionRegistry` for extensible function registration
- **Simulation**: Core data generation logic
- **Enrichment**: Treatment effect application
- **Configuration**: Parameter processing and validation
- **Storage**: Data persistence and retrieval

### 3. Mode-Based Generation
Two complementary approaches for different use cases:
- **Rule-based**: Deterministic, interpretable patterns
- **Synthesizer-based**: ML-learned patterns from real data

### 4. Reproducible Output
Seed-based deterministic generation ensures:
- Consistent results across runs
- Reliable A/B testing scenarios
- Debuggable data generation

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Configuration Layer                       │
├─────────────────────────────────────────────────────────────┤
│  config_processor.py  │  config_defaults.yaml              │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                     Simulation Layer                        │
├─────────────────────────────────────────────────────────────┤
│  simulate.py (orchestrator)                                 │
│  ├── simulate_characteristics.py                            │
│  │   ├── characteristics_rule_based.py                      │
│  │   └── characteristics_synthesizer_based.py               │
│  └── simulate_metrics.py                                    │
│      ├── metrics_rule_based.py                              │
│      └── metrics_synthesizer_based.py                       │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    Enrichment Layer                         │
├─────────────────────────────────────────────────────────────┤
│  enrich.py (orchestrator)                                   │
│  ├── enrichment.py                                          │
│  ├── enrichment_library.py                                  │
│  └── enrichment_registry.py                                 │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                     Storage Layer                           │
├─────────────────────────────────────────────────────────────┤
│  JSON/CSV export  │  Pandas DataFrames  │  Pickle models   │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Configuration Processing
```python
# config_processor.py
def load_config(config_path):
    """Load and validate configuration with defaults"""
    config = yaml.load(config_path)
    return merge_with_defaults(config)
```

### 2. Two-Phase Generation

#### Phase 1: Product Characteristics
```python
# Generate product catalog, returns JobInfo
job_info = simulate_characteristics(config)
# Output: JobInfo (products.csv saved to job directory)
products_df = load_dataframe(job_info, "products")
```

#### Phase 2: Sales Metrics
```python
# Generate sales transactions, takes JobInfo
job_info = simulate_metrics(job_info, config)
# Output: JobInfo (sales.csv saved to job directory)
sales_df = load_dataframe(job_info, "sales")
```

### 3. Optional Enrichment
```python
# Apply treatment effects
enriched_job = enrich("enrichment_config.yaml", baseline_job)
# Output: JobInfo for enriched results
```

## Generation Modes

### Rule-Based Generation

**Characteristics Generation**:
- Deterministic product creation across 8 categories
- Category-specific price ranges
- Configurable product counts per category

**Metrics Generation**:
- Daily sales probability per product
- Quantity sampling from configured distributions
- Revenue calculation (price × quantity)

**Benefits**:
- Fast execution
- Predictable patterns
- Easy to understand and debug
- No external dependencies

### Synthesizer-Based Generation

**Characteristics Generation**:
- ML model training on synthetic seed data
- Gaussian Copula or other SDV synthesizers
- Learned price-category relationships

**Metrics Generation**:
- Temporal pattern learning
- Complex correlation modeling
- Realistic sales distributions

**Benefits**:
- More sophisticated patterns
- Learned correlations
- Scalable to complex scenarios
- Research-grade synthetic data

## Backend Plugin Architecture

The simulation system uses a plugin architecture for backend dispatch, making it easy
to add new generation backends without modifying core orchestration code.

### Core Components

```python
# core/backends.py

class SimulationBackend(ABC):
    """Abstract base class for simulation backends."""

    def simulate_characteristics(self) -> pd.DataFrame:
        """Generate product characteristics."""
        ...

    def simulate_metrics(self, product_characteristics: pd.DataFrame) -> pd.DataFrame:
        """Generate metrics based on characteristics."""
        ...

    @classmethod
    def get_key(cls) -> str:
        """Config key that triggers this backend (e.g., 'RULE')."""
        ...


class BackendRegistry:
    """Registry for discovering and instantiating backends."""

    @classmethod
    def register(cls, backend_cls):
        """Register a backend class."""

    @classmethod
    def detect_backend(cls, config) -> SimulationBackend:
        """Detect and instantiate appropriate backend from config."""
```

### Built-in Backends

| Backend | Config Key | Description |
|---------|------------|-------------|
| `RuleBackend` | `RULE` | Deterministic rule-based generation |
| `SynthesizerBackend` | `SYNTHESIZER` | ML-based generation using SDV |

### Backend Detection

The system automatically detects which backend to use based on config keys:

```python
# Config with RULE key -> RuleBackend
config = {"RULE": {"CHARACTERISTICS": {...}, "METRICS": {...}}}

# Config with SYNTHESIZER key -> SynthesizerBackend
config = {"SYNTHESIZER": {"CHARACTERISTICS": {...}, "METRICS": {...}}}
```

### Adding Custom Backends

To add a new backend (e.g., CTGAN, TVAE):

```python
from online_retail_simulator.core.backends import (
    BackendRegistry,
    SimulationBackend,
)

@BackendRegistry.register
class CTGANBackend(SimulationBackend):

    @classmethod
    def get_key(cls) -> str:
        return "CTGAN"

    def simulate_characteristics(self) -> pd.DataFrame:
        # Your CTGAN implementation
        ...

    def simulate_metrics(self, product_characteristics: pd.DataFrame) -> pd.DataFrame:
        # Your CTGAN implementation
        ...
```

Once registered, use it with:

```yaml
CTGAN:
  CHARACTERISTICS:
    PARAMS: {...}
  METRICS:
    PARAMS: {...}
```

## Enrichment System

### Function Registry
The system uses a unified `FunctionRegistry` class for all extensible function types:

```python
# core/registry.py
class FunctionRegistry:
    def register(self, name, func):
        """Register function with signature validation"""

    def get(self, name):
        """Retrieve registered function (lazy loads defaults)"""

    def list(self):
        """List all registered function names"""
```

Both simulation and enrichment registries use this common infrastructure.

### Built-in Impact Functions

#### Quantity Boost
```python
def quantity_boost(sales, effect_size=0.5, enrichment_fraction=0.3,
                   enrichment_start="2024-11-15", seed=42, **kwargs):
    """Simple multiplicative increase in ordered units"""
    # Boosts ordered_units by effect_size for enriched products
    # Returns: List of modified sale dictionaries
```

#### Probability Boost
```python
def probability_boost(sales, **kwargs):
    """Increase sale probability for treated products"""
    # Same as quantity_boost (probability reflected in quantity for existing sales)
```

#### Combined Boost (Realistic)
```python
def combined_boost(sales, effect_size=0.5, ramp_days=7, enrichment_fraction=0.3,
                   enrichment_start="2024-11-15", seed=42, **kwargs):
    """Gradual rollout with partial treatment"""
    # Realistic implementation with:
    # - Gradual effect ramp-up over ramp_days
    # - Partial product treatment (enrichment_fraction)
    # - Date-based activation (enrichment_start)
    # Returns: List of modified sale dictionaries
```

## Configuration Schema

### Simulation Configuration
```yaml
SEED: 42                    # Reproducibility control (optional)

STORAGE:
  PATH: "output"            # Output directory for job results

RULE:                       # Rule-based mode settings
  CHARACTERISTICS:
    FUNCTION: simulate_characteristics_rule_based
    PARAMS:
      num_products: 100
  METRICS:
    FUNCTION: simulate_metrics_rule_based
    PARAMS:
      date_start: "2024-11-01"
      date_end: "2024-11-30"
      sale_prob: 0.7
      granularity: "daily"  # or "weekly"

SYNTHESIZER:                # ML-based mode settings (alternative to RULE)
  SYNTHESIZER_TYPE: "gaussian_copula"
  DEFAULT_PRODUCTS_ROWS: 50
  DEFAULT_SALES_ROWS: 1000
```

### Enrichment Configuration
```yaml
IMPACT:
  FUNCTION: "combined_boost"
  PARAMS:
    effect_size: 0.5
    ramp_days: 7
    enrichment_fraction: 0.3
    enrichment_start: "2024-11-15"
    seed: 42
```

## Data Schemas

For complete data schema documentation, see the [User Guide](user-guide.md).

## Extension Points

### Custom Enrichment Functions
```python
def my_custom_effect(df, my_param, **kwargs):
    """Custom treatment effect implementation"""
    # Your logic here
    return modified_df

# Register for use
from online_retail_simulator.enrich import register_enrichment_function
register_enrichment_function("my_effect", my_custom_effect)
```

### Custom Synthesizers
```python
# Extend synthesizer support
class MyCustomSynthesizer:
    def fit(self, data):
        """Train on seed data"""

    def sample(self, num_rows):
        """Generate synthetic data"""
```

## Performance Considerations

### Rule-Based Mode
- **Speed**: Very fast (< 1 second for typical datasets)
- **Memory**: Minimal (direct DataFrame creation)
- **Scalability**: Linear with product count and date range

### Synthesizer Mode
- **Speed**: Moderate (model training overhead)
- **Memory**: Higher (model storage and training)
- **Scalability**: Depends on SDV synthesizer choice

### Optimization Strategies
- Use rule-based mode for rapid prototyping
- Cache synthesizer models for repeated use
- Batch process multiple scenarios
- Lazy import SDV to reduce startup time

## Error Handling

### Configuration Validation
- Schema validation for required fields
- Type checking for parameters
- Range validation for dates and probabilities

### Graceful Degradation
- Fallback to rule-based if synthesizer fails
- Default parameter substitution
- Informative error messages

### Debugging Support
- Verbose logging options
- Intermediate output inspection
- Seed-based reproducible debugging
