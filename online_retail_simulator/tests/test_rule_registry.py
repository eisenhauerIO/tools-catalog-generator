"""Tests for the rule registry system."""

import pandas as pd
import pytest

from online_retail_simulator.simulate import (
    get_simulation_function,
    list_simulation_functions,
    register_characteristics_function,
    register_metrics_function,
)
from online_retail_simulator.simulate.rule_registry import clear_simulation_registry


def test_characteristics_function_registration():
    """Test registering and retrieving characteristics functions."""
    clear_simulation_registry()

    def dummy_characteristics(config):
        return pd.DataFrame({"asin": ["A123"], "category": ["Test"], "price": [10.0]})

    register_characteristics_function("test_chars", dummy_characteristics)

    func = get_simulation_function("characteristics", "test_chars")
    assert func == dummy_characteristics

    functions = list_simulation_functions()
    assert "test_chars" in functions["characteristics"]


def test_metrics_function_registration():
    """Test registering and retrieving metrics functions."""
    clear_simulation_registry()

    def dummy_metrics(product_characteristics, config, **kwargs):
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

    register_metrics_function("test_metrics", dummy_metrics)

    func = get_simulation_function("metrics", "test_metrics")
    assert func == dummy_metrics

    functions = list_simulation_functions()
    assert "test_metrics" in functions["metrics"]


def test_invalid_function_signatures():
    """Test that functions with invalid signatures are rejected."""
    clear_simulation_registry()

    def invalid_characteristics():  # Missing required parameters
        return pd.DataFrame()

    def invalid_metrics(wrong_param):  # Missing required parameters
        return pd.DataFrame()

    with pytest.raises(ValueError, match="must have parameters"):
        register_characteristics_function("invalid", invalid_characteristics)

    with pytest.raises(ValueError, match="must have parameters"):
        register_metrics_function("invalid", invalid_metrics)


def test_get_simulation_function():
    """Test the convenience function for getting registered functions."""
    clear_simulation_registry()

    def dummy_characteristics(config):
        return pd.DataFrame()

    def dummy_metrics(product_characteristics, config, **kwargs):
        return pd.DataFrame()

    register_characteristics_function("test_chars", dummy_characteristics)
    register_metrics_function("test_metrics", dummy_metrics)

    chars_func = get_simulation_function("characteristics", "test_chars")
    assert chars_func == dummy_characteristics

    metrics_func = get_simulation_function("metrics", "test_metrics")
    assert metrics_func == dummy_metrics

    with pytest.raises(ValueError, match="Invalid function type"):
        get_simulation_function("invalid", "test_chars")


def test_list_all_functions():
    """Test listing all registered functions."""
    clear_simulation_registry()

    def dummy_characteristics(config):
        return pd.DataFrame()

    def dummy_metrics(product_characteristics, config, **kwargs):
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
    clear_simulation_registry()

    with pytest.raises(KeyError, match="not registered"):
        get_simulation_function("characteristics", "nonexistent")

    with pytest.raises(KeyError, match="not registered"):
        get_simulation_function("metrics", "nonexistent")


def test_clear_registry():
    """Test clearing the registry."""
    clear_simulation_registry()

    def dummy_characteristics(config):
        return pd.DataFrame()

    register_characteristics_function("test", dummy_characteristics)

    functions = list_simulation_functions()
    assert "test" in functions["characteristics"]
    assert "simulate_characteristics_rule_based" in functions["characteristics"]
    assert len(functions["characteristics"]) == 2

    clear_simulation_registry()
    functions = list_simulation_functions()
    assert functions["characteristics"] == ["simulate_characteristics_rule_based"]
    assert functions["metrics"] == ["simulate_metrics_rule_based"]


def test_default_functions_registered():
    """Test that default functions are automatically registered."""
    clear_simulation_registry()

    functions = list_simulation_functions()

    assert "simulate_characteristics_rule_based" in functions["characteristics"]
    assert "simulate_metrics_rule_based" in functions["metrics"]

    chars_func = get_simulation_function("characteristics", "simulate_characteristics_rule_based")
    metrics_func = get_simulation_function("metrics", "simulate_metrics_rule_based")

    assert chars_func is not None
    assert metrics_func is not None
