"""
Rule-based simulation registry for custom user-defined simulation functions.

This module provides a registration system that allows users to register their own
rule-based simulation functions for both product characteristics and sales metrics.
The default rule-based functions are automatically registered.
"""

import importlib
import inspect
from typing import Any, Callable, Dict, List, Optional, Union

import pandas as pd

# Global registries for simulation functions
_CHARACTERISTICS_REGISTRY: Dict[str, Callable] = {}
_METRICS_REGISTRY: Dict[str, Callable] = {}

# Flag to track if defaults have been registered
_DEFAULTS_REGISTERED = False


def _register_default_functions():
    """Register the default rule-based simulation functions."""
    global _DEFAULTS_REGISTERED
    if _DEFAULTS_REGISTERED:
        return

    from .characteristics_rule_based import simulate_characteristics_rule_based
    from .metrics_rule_based import simulate_metrics_rule_based

    # Register under their actual function names
    _CHARACTERISTICS_REGISTRY["simulate_characteristics_rule_based"] = simulate_characteristics_rule_based
    _METRICS_REGISTRY["simulate_metrics_rule_based"] = simulate_metrics_rule_based
    _DEFAULTS_REGISTERED = True


class SimulationRegistry:
    """Registry for managing custom simulation functions."""

    @staticmethod
    def register_characteristics_function(name: str, func: Callable) -> None:
        """
        Register a custom characteristics generation function.

        Args:
            name: Name to register the function under
            func: Function that takes (config_path: str, config: Optional[Dict] = None) -> pd.DataFrame

        Raises:
            ValueError: If function signature is invalid
        """
        # Validate function signature
        sig = inspect.signature(func)
        required_params = {"config_path"}
        if not required_params.issubset(sig.parameters.keys()):
            raise ValueError(
                f"Function {func.__name__} must have parameters: {required_params}. "
                f"Found: {set(sig.parameters.keys())}"
            )

        # Store in registry
        _CHARACTERISTICS_REGISTRY[name] = func

    @staticmethod
    def register_metrics_function(name: str, func: Callable) -> None:
        """
        Register a custom metrics generation function.

        Args:
            name: Name to register the function under
            func: Function that takes (product_characteristics: pd.DataFrame,
                  config_path: str, **kwargs) -> pd.DataFrame

        Raises:
            ValueError: If function signature is invalid
        """
        # Validate function signature
        sig = inspect.signature(func)
        required_params = {"product_characteristics", "config_path"}
        if not required_params.issubset(sig.parameters.keys()):
            raise ValueError(
                f"Function {func.__name__} must have parameters: {required_params}. "
                f"Found: {set(sig.parameters.keys())}"
            )

        # Store in registry
        _METRICS_REGISTRY[name] = func

    @staticmethod
    def register_module(module_name: str, prefix: str = "") -> None:
        """
        Register all compatible functions from a module.

        Functions are automatically detected based on their signatures:
        - Characteristics functions: (config_path, config=None) -> DataFrame
        - Metrics functions: (product_characteristics, config_path, **kwargs) -> DataFrame

        Args:
            module_name: Name of module to import and register functions from
            prefix: Optional prefix to add to function names when registering

        Raises:
            ImportError: If module cannot be imported
        """
        # Try to import from online_retail_simulator package first
        try:
            module = importlib.import_module(f"online_retail_simulator.{module_name}")
        except (ImportError, ModuleNotFoundError):
            # Fall back to importing as standalone module
            module = importlib.import_module(module_name)

        # Register all compatible functions
        for name in dir(module):
            obj = getattr(module, name)
            if callable(obj) and not name.startswith("_"):
                try:
                    sig = inspect.signature(obj)
                    params = set(sig.parameters.keys())

                    # Check if it's a characteristics function
                    if "config_path" in params and "product_characteristics" not in params:
                        reg_name = f"{prefix}{name}" if prefix else name
                        _CHARACTERISTICS_REGISTRY[reg_name] = obj

                    # Check if it's a metrics function
                    elif "product_characteristics" in params and "config_path" in params:
                        reg_name = f"{prefix}{name}" if prefix else name
                        _METRICS_REGISTRY[reg_name] = obj

                except (ValueError, TypeError):
                    # Skip objects that don't have valid signatures
                    continue

    @staticmethod
    def get_characteristics_function(name: str) -> Callable:
        """
        Get a registered characteristics function by name.

        Args:
            name: Name of the registered function

        Returns:
            The registered function

        Raises:
            KeyError: If function is not registered
        """
        _register_default_functions()
        if name not in _CHARACTERISTICS_REGISTRY:
            raise KeyError(
                f"Characteristics function '{name}' not registered. "
                f"Available: {list(_CHARACTERISTICS_REGISTRY.keys())}"
            )
        return _CHARACTERISTICS_REGISTRY[name]

    @staticmethod
    def get_metrics_function(name: str) -> Callable:
        """
        Get a registered metrics function by name.

        Args:
            name: Name of the registered function

        Returns:
            The registered function

        Raises:
            KeyError: If function is not registered
        """
        _register_default_functions()
        if name not in _METRICS_REGISTRY:
            raise KeyError(f"Metrics function '{name}' not registered. " f"Available: {list(_METRICS_REGISTRY.keys())}")
        return _METRICS_REGISTRY[name]

    @staticmethod
    def list_characteristics_functions() -> List[str]:
        """List all registered characteristics function names."""
        _register_default_functions()
        return list(_CHARACTERISTICS_REGISTRY.keys())

    @staticmethod
    def list_metrics_functions() -> List[str]:
        """List all registered metrics function names."""
        _register_default_functions()
        return list(_METRICS_REGISTRY.keys())

    @staticmethod
    def list_all_functions() -> Dict[str, List[str]]:
        """List all registered functions by type."""
        _register_default_functions()
        return {
            "characteristics": list(_CHARACTERISTICS_REGISTRY.keys()),
            "metrics": list(_METRICS_REGISTRY.keys()),
        }

    @staticmethod
    def clear_registry() -> None:
        """Clear all registered functions (useful for testing)."""
        global _DEFAULTS_REGISTERED
        _CHARACTERISTICS_REGISTRY.clear()
        _METRICS_REGISTRY.clear()
        _DEFAULTS_REGISTERED = False


# Convenience functions for direct access
def register_characteristics_function(name: str, func: Callable) -> None:
    """Register a characteristics generation function."""
    SimulationRegistry.register_characteristics_function(name, func)


def register_metrics_function(name: str, func: Callable) -> None:
    """Register a metrics generation function."""
    SimulationRegistry.register_metrics_function(name, func)


def register_simulation_module(module_name: str, prefix: str = "") -> None:
    """Register all compatible functions from a module."""
    SimulationRegistry.register_module(module_name, prefix)


def list_simulation_functions() -> Dict[str, List[str]]:
    """List all registered simulation functions."""
    return SimulationRegistry.list_all_functions()


def get_simulation_function(func_type: str, name: str) -> Callable:
    """
    Get a registered simulation function.

    Args:
        func_type: Type of function ('characteristics' or 'metrics')
        name: Name of the function

    Returns:
        The registered function
    """
    if func_type == "characteristics":
        return SimulationRegistry.get_characteristics_function(name)
    elif func_type == "metrics":
        return SimulationRegistry.get_metrics_function(name)
    else:
        raise ValueError(f"Invalid function type: {func_type}. Must be 'characteristics' or 'metrics'")
