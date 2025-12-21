"""Tests for enrichment function registration."""

import os
import tempfile

import pytest

from online_retail_simulator import (
    clear_enrichment_registry,
    enrich,
    list_enrichment_functions,
    load_dataframe,
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
    with pytest.raises(ValueError, match="must have parameters"):
        register_enrichment_function("bad_function", bad_function)


def test_register_module():
    """Test module registration."""
    # Clear registry first
    clear_enrichment_registry()

    # Register the enrichment library module
    register_enrichment_module("enrich.enrichment_library")

    # Should have registered the built-in functions
    registered = list_enrichment_functions()
    assert "quantity_boost" in registered
    assert "combined_boost" in registered
    assert "probability_boost" in registered


def test_use_registered_function():
    """Test using a registered function in enrichment."""

    def double_quantity(sales, **kwargs):
        """Double the ordered units of all sales."""
        for sale in sales:
            sale["ordered_units"] = sale["ordered_units"] * 2
            unit_price = sale.get("unit_price", sale.get("price"))
            sale["revenue"] = round(sale["ordered_units"] * unit_price, 2)
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
        job_info = simulate(test_config_path)

        # Load original sales before enrichment
        original_sales = load_dataframe(job_info, "sales")

        # Apply enrichment using registered function
        enriched_job_info = enrich(config_path, job_info)

        # Load enriched results
        enriched_sales = load_dataframe(enriched_job_info, "enriched")

        # Verify doubling effect
        original_total = original_sales["ordered_units"].sum()
        enriched_total = enriched_sales["ordered_units"].sum()

        assert enriched_total == original_total * 2

    finally:
        os.unlink(config_path)


@pytest.mark.xfail(reason="Registry precedence over built-in functions needs investigation")
def test_registry_precedence():
    """Test that registry takes precedence over module loading."""

    # Clear registry first to ensure clean state
    clear_enrichment_registry()

    def custom_quantity_boost(sales, **kwargs):
        """Custom version that triples all quantities."""
        import copy

        treated_sales = []
        for sale in sales:
            sale_copy = copy.deepcopy(sale)
            sale_copy["quantity"] = sale_copy["quantity"] * 3
            unit_price = sale_copy.get("unit_price", sale_copy.get("price"))
            sale_copy["revenue"] = round(sale_copy["quantity"] * unit_price, 2)
            treated_sales.append(sale_copy)
        return treated_sales

    # Register function with same name as built-in
    register_enrichment_function("quantity_boost", custom_quantity_boost)

    # Verify it was registered
    functions = list_enrichment_functions()
    assert "quantity_boost" in functions

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
        job_info = simulate(test_config_path)

        # Load original sales before enrichment
        original_sales = load_dataframe(job_info, "sales")

        # Apply enrichment - should use registered version (triple)
        enriched_job_info = enrich(config_path, job_info)

        # Load enriched results
        enriched_sales = load_dataframe(enriched_job_info, "enriched")

        # Verify tripling effect (not the built-in boost)
        original_total = original_sales["quantity"].sum()
        enriched_total = enriched_sales["quantity"].sum()

        assert enriched_total == original_total * 3

    finally:
        os.unlink(config_path)


def test_list_functions():
    """Test listing registered functions."""
    # Clear registry
    clear_enrichment_registry()

    # After clear, list() triggers lazy loading of defaults
    defaults = list_enrichment_functions()
    assert len(defaults) == 3  # quantity_boost, probability_boost, combined_boost

    # Register some custom functions
    def func1(sales, **kwargs):
        return sales

    def func2(sales, **kwargs):
        return sales

    register_enrichment_function("func1", func1)
    register_enrichment_function("func2", func2)

    # Should list defaults + custom
    functions = list_enrichment_functions()
    assert "func1" in functions
    assert "func2" in functions
    assert "quantity_boost" in functions
    assert len(functions) == 5  # 3 defaults + 2 custom


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
    from online_retail_simulator.enrich.enrichment_registry import _enrichment_registry

    result = _enrichment_registry.get("test_func")([], test="value")
    assert result == [{"test": "second"}]
