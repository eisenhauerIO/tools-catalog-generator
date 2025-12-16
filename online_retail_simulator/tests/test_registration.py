"""Tests for enrichment function registration."""

import os
import tempfile

import pandas as pd
import pytest

from online_retail_simulator import (
    enrich,
    list_enrichment_functions,
    register_enrichment_function,
    register_enrichment_module,
    simulate,
)


def test_register_function_direct():
    """Test direct function registration."""

    def test_effect(sales, **kwargs):
        """Simple test effect."""
        multiplier = kwargs.get("multiplier", 1.5)
        for sale in sales:
            sale["quantity"] = int(sale["quantity"] * multiplier)
        return sales

    # Register function
    register_enrichment_function("test_effect", test_effect)

    # Verify it's registered
    assert "test_effect" in list_enrichment_functions()


def test_register_function_invalid_signature():
    """Test registration with invalid function signature."""

    def bad_function(data, **kwargs):  # Missing 'sales' parameter
        return data

    # Should raise error for invalid signature
    with pytest.raises(ValueError, match="must have 'sales' parameter"):
        register_enrichment_function("bad_function", bad_function)


def test_register_module():
    """Test module registration."""
    # Clear registry first
    from online_retail_simulator.enrichment_application import _ENRICHMENT_REGISTRY

    _ENRICHMENT_REGISTRY.clear()

    # Register the impact library module
    register_enrichment_module("enrichment_impact_library")

    # Should have registered the built-in functions
    registered = list_enrichment_functions()
    assert "quantity_boost" in registered
    assert "combined_boost" in registered
    assert "probability_boost" in registered


def test_use_registered_function():
    """Test using a registered function in enrichment."""

    def double_quantity(sales, **kwargs):
        """Double the quantity of all sales."""
        for sale in sales:
            sale["quantity"] = sale["quantity"] * 2
            unit_price = sale.get("unit_price", sale.get("price"))
            sale["revenue"] = round(sale["quantity"] * unit_price, 2)
        return sales

    # Register function
    register_enrichment_function("double_quantity", double_quantity)

    # Create test config
    config_content = """
IMPACT:
  FUNCTION: "double_quantity"
  PARAMS: {}
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(config_content)
        config_path = f.name

    try:
        # Generate test data
        test_config_path = os.path.join(os.path.dirname(__file__), "config_rule.yaml")
        sales_df = simulate(test_config_path)

        # Apply enrichment using registered function
        enriched_df = enrich(config_path, sales_df)

        # Verify doubling effect
        original_total = sales_df["quantity"].sum()
        enriched_total = enriched_df["quantity"].sum()

        assert enriched_total == original_total * 2

    finally:
        os.unlink(config_path)


def test_registry_precedence():
    """Test that registry takes precedence over module loading."""

    def custom_quantity_boost(sales, **kwargs):
        """Custom version that triples instead of normal boost."""
        for sale in sales:
            sale["quantity"] = sale["quantity"] * 3
            unit_price = sale.get("unit_price", sale.get("price"))
            sale["revenue"] = round(sale["quantity"] * unit_price, 2)
        return sales

    # Register function with same name as built-in
    register_enrichment_function("quantity_boost", custom_quantity_boost)

    # Create test config using quantity_boost
    config_content = """
IMPACT:
  FUNCTION: "quantity_boost"
  PARAMS: {}
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(config_content)
        config_path = f.name

    try:
        # Generate test data
        test_config_path = os.path.join(os.path.dirname(__file__), "config_rule.yaml")
        sales_df = simulate(test_config_path)

        # Apply enrichment - should use registered version (triple)
        enriched_df = enrich(config_path, sales_df)

        # Verify tripling effect (not the built-in boost)
        original_total = sales_df["quantity"].sum()
        enriched_total = enriched_df["quantity"].sum()

        assert enriched_total == original_total * 3

    finally:
        os.unlink(config_path)


def test_list_functions():
    """Test listing registered functions."""
    # Clear registry
    from online_retail_simulator.enrichment_application import _ENRICHMENT_REGISTRY

    _ENRICHMENT_REGISTRY.clear()

    # Should be empty initially
    assert list_enrichment_functions() == []

    # Register some functions
    def func1(sales, **kwargs):
        return sales

    def func2(sales, **kwargs):
        return sales

    register_enrichment_function("func1", func1)
    register_enrichment_function("func2", func2)

    # Should list both
    functions = list_enrichment_functions()
    assert "func1" in functions
    assert "func2" in functions
    assert len(functions) == 2


def test_register_function_overwrites():
    """Test that registering same name overwrites previous function."""

    def first_func(sales, **kwargs):
        return [{"test": "first"}]

    def second_func(sales, **kwargs):
        return [{"test": "second"}]

    # Register first function
    register_enrichment_function("test_func", first_func)

    # Register second function with same name
    register_enrichment_function("test_func", second_func)

    # Should only have one entry
    functions = list_enrichment_functions()
    count = sum(1 for f in functions if f == "test_func")
    assert count == 1

    # Should use the second function
    from online_retail_simulator.enrichment_application import _ENRICHMENT_REGISTRY

    result = _ENRICHMENT_REGISTRY["test_func"]([], test="value")
    assert result == [{"test": "second"}]
