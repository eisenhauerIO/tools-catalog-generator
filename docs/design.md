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
# Generate product catalog
products_df = simulate_characteristics(config)
# Output: DataFrame with asin, category, price columns
```

#### Phase 2: Sales Metrics
```python
# Generate sales transactions
sales_df = simulate_metrics(products_df, config)
# Output: DataFrame with asin, date, quantity, revenue columns
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

## Enrichment System

### Impact Function Registry
```python
# enrichment_registry.py
class EnrichmentRegistry:
    def register_function(self, name, func):
        """Register custom enrichment functions"""

    def get_function(self, name):
        """Retrieve registered functions"""
```

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
