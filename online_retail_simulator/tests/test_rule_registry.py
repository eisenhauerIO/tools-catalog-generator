"""Tests for the rule registry system."""

import pandas as pd
import pytest

from online_retail_simulator.simulate import (
    get_simulation_function,
    list_simulation_functions,
    register_characteristics_function,
    register_metrics_function,
    register_simulation_module,
)
from online_retail_simulator.simulate.rule_registry import SimulationRegistry


def test_characteristics_function_registration():
    """Test registering and retrieving characteristics functions."""
    # Clear registry for clean test
    SimulationRegistry.clear_registry()

    def dummy_characteristics(config_path, config=None):
        return pd.DataFrame({"asin": ["A123"], "category": ["Test"], "price": [10.0]})

    # Test registration
    register_characteristics_function("test_chars", dummy_characteristics)

    # Test retrieval
    func = SimulationRegistry.get_characteristics_function("test_chars")
    assert func == dummy_characteristics

    # Test listing
    functions = SimulationRegistry.list_characteristics_functions()
    assert "test_chars" in functions


def test_metrics_function_registration():
    """Test registering and retrieving metrics functions."""
    # Clear registry for clean test
    SimulationRegistry.clear_registry()

    def dummy_metrics(product_characteristics, config_path, **kwargs):
        return pd.DataFrame(
            {
                "asin": ["A123"],
                "category": ["Test"],
                "price": [10.0],
                "date": ["2024-01-01"],
                "quantity": [1],
                "revenue": [10.0],
            }
        )

    # Test registration
    register_metrics_function("test_metrics", dummy_metrics)

    # Test retrieval
    func = SimulationRegistry.get_metrics_function("test_metrics")
    assert func == dummy_metrics

    # Test listing
    functions = SimulationRegistry.list_metrics_functions()
    assert "test_metrics" in functions


def test_invalid_function_signatures():
    """Test that functions with invalid signatures are rejected."""
    # Clear registry for clean test
    SimulationRegistry.clear_registry()

    def invalid_characteristics():  # Missing required parameters
        return pd.DataFrame()

    def invalid_metrics(wrong_param):  # Missing required parameters
        return pd.DataFrame()

    # Test that invalid functions raise errors
    with pytest.raises(ValueError, match="must have parameters"):
        register_characteristics_function("invalid", invalid_characteristics)

    with pytest.raises(ValueError, match="must have parameters"):
        register_metrics_function("invalid", invalid_metrics)


def test_get_simulation_function():
    """Test the convenience function for getting registered functions."""
    # Clear registry for clean test
    SimulationRegistry.clear_registry()

    def dummy_characteristics(config_path, config=None):
        return pd.DataFrame()

    def dummy_metrics(product_characteristics, config_path, **kwargs):
        return pd.DataFrame()

    register_characteristics_function("test_chars", dummy_characteristics)
    register_metrics_function("test_metrics", dummy_metrics)

    # Test retrieval by type
    chars_func = get_simulation_function("characteristics", "test_chars")
    assert chars_func == dummy_characteristics

    metrics_func = get_simulation_function("metrics", "test_metrics")
    assert metrics_func == dummy_metrics

    # Test invalid type
    with pytest.raises(ValueError, match="Invalid function type"):
        get_simulation_function("invalid", "test_chars")


def test_list_all_functions():
    """Test listing all registered functions."""
    # Clear registry for clean test
    SimulationRegistry.clear_registry()

    def dummy_characteristics(config_path, config=None):
        return pd.DataFrame()

    def dummy_metrics(product_characteristics, config_path, **kwargs):
        return pd.DataFrame()

    register_characteristics_function("test_chars", dummy_characteristics)
    register_metrics_function("test_metrics", dummy_metrics)

    all_functions = list_simulation_functions()

    assert "characteristics" in all_functions
    assert "metrics" in all_functions
    assert "test_chars" in all_functions["characteristics"]
    assert "test_metrics" in all_functions["metrics"]


def test_function_not_found():
    """Test error handling for non-existent functions."""
    # Clear registry for clean test
    SimulationRegistry.clear_registry()

    with pytest.raises(KeyError, match="not registered"):
        SimulationRegistry.get_characteristics_function("nonexistent")

    with pytest.raises(KeyError, match="not registered"):
        SimulationRegistry.get_metrics_function("nonexistent")


def test_clear_registry():
    """Test clearing the registry."""
    # Clear registry for clean test
    SimulationRegistry.clear_registry()

    def dummy_characteristics(config_path, config=None):
        return pd.DataFrame()

    register_characteristics_function("test", dummy_characteristics)

    # Verify function is registered (should have "test" + actual names)
    functions = SimulationRegistry.list_characteristics_functions()
    assert "test" in functions
    assert "simulate_characteristics_rule_based" in functions
    assert len(functions) == 2

    # Clear and verify only defaults remain
    SimulationRegistry.clear_registry()
    functions = SimulationRegistry.list_all_functions()
    assert functions["characteristics"] == [
        "simulate_characteristics_rule_based",
    ]
    assert functions["metrics"] == ["simulate_metrics_rule_based"]


def test_default_functions_registered():
    """Test that default functions are automatically registered."""
    # Clear registry first
    SimulationRegistry.clear_registry()

    # Getting functions should trigger default registration
    functions = SimulationRegistry.list_all_functions()

    assert "simulate_characteristics_rule_based" in functions["characteristics"]
    assert "simulate_metrics_rule_based" in functions["metrics"]

    # Verify we can get the actual functions
    chars_func = SimulationRegistry.get_characteristics_function("simulate_characteristics_rule_based")
    metrics_func = SimulationRegistry.get_metrics_function("simulate_metrics_rule_based")

    assert chars_func is not None
    assert metrics_func is not None
