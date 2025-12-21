# Extensibility & Maintainability Improvement Roadmap

## Overview

This document provides **design recommendations** for architectural improvements to enhance the extensibility and maintainability of the online-retail-simulator codebase. These are suggestions for future work, not immediate implementation tasks.

The focus is on reducing coupling, improving consistency, and making the system easier to extend without changing core functionality. Deprecation warnings are acceptable for transitioning to new patterns.

## Current State Assessment

**Strengths:**
- Clean module separation (simulate/, enrich/, manage/)
- Working registration system for custom functions
- Comprehensive test coverage (9+ test files)
- Good documentation and demos

**Key Issues Identified:**
1. **Dual registry implementations** with inconsistent patterns between `SimulationRegistry` and `EnrichmentRegistry`
2. **Hard-coded backend dispatch logic** (RULE vs SYNTHESIZER) scattered across characteristics.py and metrics.py
3. **Inconsistent function signatures** across different function types
4. **No type hints** making code harder to understand and maintain
5. **Global state management** with manual `_DEFAULTS_REGISTERED` flags
6. **Tight coupling** between config processing and validation logic

## Implementation Strategy

### Phase 1: Foundation & Type Safety (Weeks 1-2)

#### 1.1 Add Type Hints and Protocols
**Priority: HIGH | Risk: LOW | Effort: 4-6 days**

Create a new module with type definitions and protocols for all extension points:

**New file:** `online_retail_simulator/core/types.py`
- Define `Protocol` classes for each function type:
  - `CharacteristicsFunction` - takes `(config: Dict)` → `DataFrame`
  - `MetricsFunction` - takes `(product_characteristics: DataFrame, config: Dict)` → `DataFrame`
  - `EnrichmentFunction` - takes `(sales: list, **kwargs)` → `list`
- Define `TypedDict` structures for config sections
- Add type aliases for common patterns

**Updated files:**
- Add type hints to all public functions in `__init__.py`
- Add type hints to registry methods in `simulate/rule_registry.py` and `enrich/enrichment_registry.py`
- Add type hints to `config_processor.py`

**Benefits:**
- Self-documenting code
- IDE autocomplete and type checking
- Foundation for runtime validation
- Easier onboarding for developers

#### 1.2 Custom Exception Hierarchy
**Priority: HIGH | Risk: LOW | Effort: 2-3 days**

Create consistent error handling across the codebase:

**New file:** `online_retail_simulator/core/exceptions.py`
- `SimulatorError` - Base exception
- `ConfigurationError` - Invalid config (with context: config_path, field)
- `RegistryError` - Registry operations failed (with context: function_name, registry_type)
- `BackendError` - Backend operations failed
- `ValidationError` - Parameter validation failed

**Updated files:**
- Replace generic `ValueError`, `KeyError` with specific exceptions throughout:
  - `simulate/rule_registry.py`
  - `enrich/enrichment_registry.py`
  - `config_processor.py`
  - `simulate/characteristics.py`
  - `simulate/metrics.py`

**Benefits:**
- Consistent error messages
- Better debugging with structured context
- Users can catch specific error types
- Foundation for error recovery

### Phase 2: Core Architecture (Weeks 3-5)

#### 2.1 Unified Registry Framework ✅ COMPLETED
**Priority: HIGH | Risk: LOW-MEDIUM | Effort: 5-7 days**

**Status**: Implemented. Created `online_retail_simulator/core/registry.py` with unified `FunctionRegistry` class. Both simulation and enrichment registries now use this framework.

Replace dual registry implementations with a unified, generic framework:

**New file:** `online_retail_simulator/core/registry.py`
- `FunctionRegistry` - Generic registry with validation
- Built-in support for lazy default loading, module registration
- Eliminates global `_DEFAULTS_REGISTERED` flags

**Refactored files:**
- `simulate/rule_registry.py` - Uses two `FunctionRegistry` instances
- `enrich/enrichment_registry.py` - Uses one `FunctionRegistry` instance
- Convenience functions delegate to registry instances

**Benefits achieved:**
- Single source of truth for registry logic
- Consistent behavior across all function types
- Easier to add new function types in future
- Better testability

#### 2.2 Backend Plugin Architecture ✅ COMPLETED
**Priority: HIGH | Risk: MEDIUM | Effort: 5-7 days**

**Status**: Implemented. Created `online_retail_simulator/core/backends.py` with `SimulationBackend` abstract base class and `BackendRegistry`. Rule and Synthesizer backends now use this framework.

Replace hard-coded dispatch logic with a plugin system:

**New file:** `online_retail_simulator/core/backends.py`
- `SimulationBackend` abstract base class with methods:
  - `simulate_characteristics(config)` → `DataFrame`
  - `simulate_metrics(products, config)` → `DataFrame`
  - `validate_config(config)` → `None`
  - `get_name()` → `str`
- `BackendRegistry` for managing backends
- `RuleBasedBackend` - encapsulates current RULE logic
- `SynthesizerBackend` - encapsulates current SYNTHESIZER logic

**Refactored files:**
- `simulate/characteristics.py` - Simplify to backend detection and dispatch
- `simulate/metrics.py` - Simplify to backend detection and dispatch
- Move implementation logic into backend classes

**Before:**
```python
# Hard-coded if/elif chains in characteristics.py
if "RULE" in config:
    # ... get function from registry
    return func(config)
elif "SYNTHESIZER" in config:
    if function_name != "gaussian_copula":
        raise NotImplementedError(...)
    from .characteristics_synthesizer_based import ...
    return ...
```

**After:**
```python
# Clean dispatch in characteristics.py
backend = BackendRegistry.detect_backend(config)
return backend.simulate_characteristics(config)
```

**Benefits:**
- Easy to add new backends (TVAE, CTGAN, etc.)
- Clear extension point for users
- Backend-specific logic encapsulated
- Better testing (mock backends)

#### 2.3 Configuration Validation Framework
**Priority: MEDIUM | Risk: LOW | Effort: 3-4 days**

Decouple validation from config_defaults.yaml structure:

**New file:** `online_retail_simulator/core/validation.py`
- `ParameterSchema` dataclass for defining parameter requirements
- `FunctionValidator` base class for parameter validation
- `ValidatorRegistry` for managing validators
- Validators for built-in functions

**Refactored files:**
- `config_processor.py` - Use validator registry instead of extracting schemas from defaults
- Delegate backend-specific validation to backends

**Benefits:**
- Custom functions can provide optional validators
- Clear separation between defaults and validation
- Better error messages with parameter descriptions
- Foundation for auto-generating documentation

### Phase 3: Refinement (Weeks 6-7)

#### 3.1 Configuration Processing Refactor
**Priority: MEDIUM | Risk: LOW | Effort: 3-4 days**

Separate concerns in configuration handling:

**Refactored file:** `config_processor.py`
- Create `ConfigProcessor` class with distinct phases:
  - `load_config()` - Load YAML/JSON files
  - `merge_with_defaults()` - Deep merge logic
  - `validate()` - Delegate to validators
  - `process()` - Full pipeline
- Support for multiple config formats via strategy pattern
- Keep `process_config()` as backward-compatible wrapper

**Benefits:**
- Single Responsibility Principle
- Easy to add new config formats (TOML, etc.)
- Testable in isolation
- Can bypass validation for performance if needed

#### 3.2 Testing Infrastructure
**Priority: LOW-MEDIUM | Risk: VERY LOW | Effort: 2-3 days**

Create reusable testing utilities:

**New file:** `online_retail_simulator/testing/__init__.py`
- `SimulatorTestCase` base class with fixtures:
  - `create_sample_config()` - Generate test configs
  - `create_temp_config()` - Create temporary config files
  - `create_sample_products()` - Sample product data
  - `create_sample_sales()` - Sample sales data
- `RegistryTestMixin` for registry-specific tests
- `MockBackend` for testing without actual data generation

**Benefits:**
- Reduces test code duplication
- Easier to write tests for custom functions
- Better test isolation
- Foundation for testing best practices guide

### Phase 4: Polish (Week 8)

#### 4.1 Introspection and Documentation
**Priority: LOW | Risk: VERY LOW | Effort: 1-2 days**

Add runtime introspection capabilities:

**Enhanced registry methods:**
- `describe(name)` → `FunctionMetadata` (name, docstring, signature, module)
- `list_with_descriptions()` → List of metadata dicts
- `FunctionMetadata` class for structured function information

**Optional:** Create CLI tool for introspection
- `python -m online_retail_simulator --list-functions characteristics`
- Interactive exploration in notebooks

**Benefits:**
- Better discoverability
- Self-documenting code
- Easier debugging
- Foundation for auto-docs

## Critical Files for Implementation

### New Files (7)
1. `online_retail_simulator/core/__init__.py`
2. `online_retail_simulator/core/types.py` - Type definitions and protocols
3. `online_retail_simulator/core/exceptions.py` - Exception hierarchy
4. `online_retail_simulator/core/registry.py` - Unified registry framework
5. `online_retail_simulator/core/backends.py` - Backend plugin system
6. `online_retail_simulator/core/validation.py` - Validation framework
7. `online_retail_simulator/testing/__init__.py` - Testing utilities

### Files to Refactor (6)
1. `online_retail_simulator/simulate/rule_registry.py` - Migrate to new registry
2. `online_retail_simulator/enrich/enrichment_registry.py` - Migrate to new registry
3. `online_retail_simulator/config_processor.py` - Separate config loading/validation
4. `online_retail_simulator/simulate/characteristics.py` - Use backend system
5. `online_retail_simulator/simulate/metrics.py` - Use backend system
6. `online_retail_simulator/__init__.py` - Add type hints

### Files to Update (extensive type hints)
- All test files (use new testing utilities)
- All simulation functions (add type hints)
- Documentation (reflect new architecture)

## Implementation Guidelines

### Backward Compatibility
- Keep existing public APIs unchanged
- Add new functionality alongside old
- Deprecation warnings where needed
- Migration guide for custom function authors

### Testing Strategy
- All existing tests must pass
- Add tests for new components as they're built
- Integration tests for backward compatibility
- Pre-commit hooks must pass throughout

### Risk Mitigation
1. **Phase 1 (Type hints, exceptions)** - Low risk, additive changes
2. **Phase 2 (Core architecture)** - Keep old code alongside new with feature flags
3. **Phase 3 (Refinement)** - Wrap existing logic, minimal changes
4. **Phase 4 (Polish)** - Optional enhancements, can defer

### Success Criteria
- Zero breaking changes to public API
- All existing tests pass
- Type hints coverage >90%
- Can add new backend in <1 day
- Can add new function type in <2 hours
- Reduced code duplication by ~20%
- Consistent error handling throughout

## Rollout Plan

### Week 1-2: Foundation
- Create `core/` directory structure
- Implement `types.py` with all protocols
- Implement `exceptions.py`
- Add type hints to `__init__.py`, registries, config_processor
- Update tests to use new exceptions

### Week 3-4: Registry & Backend
- Implement `core/registry.py`
- Create adapter layer for existing registries
- Implement `core/backends.py`
- Refactor `characteristics.py` and `metrics.py`
- Extensive testing

### Week 5: Validation
- Implement `core/validation.py`
- Migrate validation from `config_processor.py`
- Add validators for built-in functions

### Week 6-7: Refinement
- Refactor `config_processor.py` into class-based design
- Create `testing/__init__.py`
- Migrate tests to use new utilities

### Week 8: Polish
- Add introspection to registries
- Update documentation
- Create migration guide
- Optional CLI tool

## How to Use This Roadmap

This document serves as a **reference for future architectural improvements**. When you're ready to work on extensibility/maintainability:

1. **Pick a priority area** based on current pain points:
   - Struggling to add new backends? → Start with Phase 2.2 (Backend Plugin Architecture)
   - Custom function registration confusing? → Start with Phase 2.1 (Unified Registry)
   - Type errors and unclear APIs? → Start with Phase 1.1 (Type Hints)
   - Inconsistent error messages? → Start with Phase 1.2 (Exception Hierarchy)

2. **Implement incrementally**:
   - Each item can be done independently
   - Start with one vertical slice (e.g., registry refactor) as a reference pattern
   - Deprecation warnings are acceptable for transitioning to new patterns

3. **Test thoroughly**:
   - Existing tests should continue to pass
   - Add new tests for new abstractions
   - Pre-commit hooks must pass

4. **Update documentation**:
   - Reflect new patterns in developer docs
   - Provide migration examples for custom function authors
   - Update API reference

## When to Revisit This Plan

Consider implementing these improvements when:
- Adding a new backend becomes too complex
- Custom function registration causes confusion
- Error messages are unclear or inconsistent
- Code duplication increases
- New contributors struggle with architecture

## Summary of Key Recommendations

**Highest Impact:**
1. **Unified Registry Framework** - Eliminates duplication, makes adding new function types easy
2. **Backend Plugin Architecture** - Makes adding new ML models or data generation strategies straightforward
3. **Type Hints & Protocols** - Improves IDE support, catches errors early, documents contracts

**Foundation for Future:**
4. **Exception Hierarchy** - Better error messages and debugging
5. **Validation Framework** - Cleaner separation of concerns
6. **Testing Utilities** - Easier to test custom extensions

This roadmap is designed to be executed incrementally with low risk to the existing codebase while significantly improving extensibility and maintainability over time.
