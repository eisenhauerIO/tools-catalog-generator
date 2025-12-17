"""Tests for the enrichment registry system."""

import pytest

from online_retail_simulator.enrichment_application import (
    clear_enrichment_registry,
    list_enrichment_functions,
    load_effect_function,
    register_enrichment_function,
)


def test_default_enrichment_functions_registered():
    """Test that default enrichment functions are automatically registered."""
    # Clear registry first
    clear_enrichment_registry()

    # Getting functions should trigger default registration
    functions = list_enrichment_functions()

    assert "quantity_boost" in functions
    assert "probability_boost" in functions
    assert "combined_boost" in functions

    # Verify we can get the default functions
    quantity_func = load_effect_function("", "quantity_boost")
    combined_func = load_effect_function("", "combined_boost")

    assert quantity_func is not None
    assert combined_func is not None


def test_custom_enrichment_function_registration():
    """Test registering and retrieving custom enrichment functions."""
    # Clear registry for clean test
    clear_enrichment_registry()

    def dummy_enrichment(sales, **kwargs):
        return sales

    # Test registration
    register_enrichment_function("test_enrichment", dummy_enrichment)

    # Test retrieval
    func = load_effect_function("", "test_enrichment")
    assert func == dummy_enrichment

    # Test listing (should include both custom and defaults)
    functions = list_enrichment_functions()
    assert "test_enrichment" in functions
    assert "quantity_boost" in functions  # Default should also be there


def test_invalid_enrichment_function_signature():
    """Test that functions with invalid signatures are rejected."""
    # Clear registry for clean test
    clear_enrichment_registry()

    def invalid_enrichment():  # Missing required 'sales' parameter
        return []

    # Test that invalid function raises error
    with pytest.raises(ValueError, match="must have 'sales' parameter"):
        register_enrichment_function("invalid", invalid_enrichment)


def test_enrichment_function_not_found():
    """Test error handling for non-existent enrichment functions."""
    # Clear registry for clean test
    clear_enrichment_registry()

    with pytest.raises(KeyError, match="not registered"):
        load_effect_function("", "nonexistent_function")


def test_clear_enrichment_registry():
    """Test clearing the enrichment registry."""
    # Clear registry for clean test
    clear_enrichment_registry()

    def dummy_enrichment(sales, **kwargs):
        return sales

    register_enrichment_function("test", dummy_enrichment)

    # Verify function is registered (should have "test" + defaults)
    functions = list_enrichment_functions()
    assert "test" in functions
    assert "quantity_boost" in functions
    assert len(functions) >= 4  # test + 3 defaults

    # Clear and verify only defaults remain
    clear_enrichment_registry()
    functions = list_enrichment_functions()
    assert "test" not in functions
    assert "quantity_boost" in functions  # Defaults should be re-registered
    assert len(functions) == 3  # Only the 3 defaults


def test_backward_compatibility_with_module_parameter():
    """Test that the module parameter is ignored but doesn't break anything."""
    # Clear registry for clean test
    clear_enrichment_registry()

    # Should work regardless of module parameter
    func1 = load_effect_function("enrichment_impact_library", "quantity_boost")
    func2 = load_effect_function("some_other_module", "quantity_boost")
    func3 = load_effect_function("", "quantity_boost")

    # All should return the same function
    assert func1 == func2 == func3
