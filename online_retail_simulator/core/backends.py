"""
Backend plugin architecture for simulation.

Provides abstract base class and registry for simulation backends.
Backends encapsulate the logic for generating characteristics and metrics.
"""

from abc import ABC, abstractmethod
from typing import Dict, Type

import pandas as pd


class SimulationBackend(ABC):
    """Abstract base for simulation backends."""

    def __init__(self, backend_config: dict):
        self.config = backend_config

    @abstractmethod
    def simulate_characteristics(self) -> pd.DataFrame:
        """Generate product characteristics."""
        ...

    @abstractmethod
    def simulate_metrics(self, product_characteristics: pd.DataFrame) -> pd.DataFrame:
        """
        Generate metrics.

        TODO: Some backends ignore product_characteristics. Revisit when
        synthesizer backend evolves to use characteristics as conditioning input.
        """
        ...

    @classmethod
    @abstractmethod
    def get_key(cls) -> str:
        """Config key that triggers this backend (e.g., 'RULE', 'SYNTHESIZER')."""
        ...


class BackendRegistry:
    """Registry for simulation backends."""

    _backends: Dict[str, Type[SimulationBackend]] = {}

    @classmethod
    def register(cls, backend_cls: Type[SimulationBackend]):
        """Register a backend class."""
        cls._backends[backend_cls.get_key()] = backend_cls
        return backend_cls

    @classmethod
    def detect_backend(cls, config: dict) -> SimulationBackend:
        """Detect and instantiate the appropriate backend from config."""
        for key, backend_cls in cls._backends.items():
            if key in config:
                return backend_cls(config[key])
        available = list(cls._backends.keys())
        raise ValueError(f"Config must contain one of: {available}")


@BackendRegistry.register
class RuleBackend(SimulationBackend):
    """Rule-based simulation backend using registered functions."""

    @classmethod
    def get_key(cls) -> str:
        return "RULE"

    def simulate_characteristics(self) -> pd.DataFrame:
        from ..simulate.rule_registry import get_simulation_function

        characteristics_config = self.config["CHARACTERISTICS"]
        function_name = characteristics_config.get("FUNCTION")
        func = get_simulation_function("characteristics", function_name)
        return func({"RULE": self.config})

    def simulate_metrics(self, product_characteristics: pd.DataFrame) -> pd.DataFrame:
        from ..simulate.rule_registry import get_simulation_function

        metrics_config = self.config["METRICS"]
        function_name = metrics_config.get("FUNCTION")
        func = get_simulation_function("metrics", function_name)
        return func(product_characteristics, {"RULE": self.config})


@BackendRegistry.register
class SynthesizerBackend(SimulationBackend):
    """Synthesizer-based simulation backend using SDV."""

    @classmethod
    def get_key(cls) -> str:
        return "SYNTHESIZER"

    def simulate_characteristics(self) -> pd.DataFrame:
        from ..simulate.characteristics_synthesizer_based import (
            simulate_characteristics_synthesizer_based,
        )

        return simulate_characteristics_synthesizer_based({"SYNTHESIZER": self.config})

    def simulate_metrics(self, product_characteristics: pd.DataFrame) -> pd.DataFrame:
        # TODO: Currently ignores product_characteristics. Revisit when synthesizer
        # evolves to condition metrics generation on characteristics.
        from ..simulate.metrics_synthesizer_based import (
            simulate_metrics_synthesizer_based,
        )

        return simulate_metrics_synthesizer_based(product_characteristics, {"SYNTHESIZER": self.config})
