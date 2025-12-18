"""Configuration processing with defaults and validation."""

import copy
import json
from pathlib import Path
from typing import Any, Dict, Set

import yaml


def _extract_param_schemas_from_defaults() -> Dict[str, Any]:
    """Extract parameter schemas from config defaults."""
    defaults = load_defaults()
    schemas = {}

    for backend in ["RULE", "SYNTHESIZER"]:
        if backend in defaults:
            schemas[backend] = {}
            backend_config = defaults[backend]

            for section in ["CHARACTERISTICS", "METRICS"]:
                if section in backend_config:
                    schemas[backend][section] = {}
                    section_config = backend_config[section]
                    function_name = section_config.get("FUNCTION")
                    params = section_config.get("PARAMS", {})

                    if function_name and params:
                        schemas[backend][section][function_name] = set(params.keys())

    return schemas


def _get_param_schemas() -> Dict[str, Any]:
    """Get parameter schemas, cached for performance."""
    if not hasattr(_get_param_schemas, "_cache"):
        _get_param_schemas._cache = _extract_param_schemas_from_defaults()
    return _get_param_schemas._cache


def load_defaults() -> Dict[str, Any]:
    """Load default configuration from package."""
    defaults_path = Path(__file__).parent / "config_defaults.yaml"
    with open(defaults_path, "r") as f:
        return yaml.safe_load(f)


def deep_merge(base: Dict, override: Dict) -> Dict:
    """
    Deep merge two dictionaries, with override values taking precedence.

    Args:
        base: Base dictionary (defaults)
        override: Override dictionary (user config)

    Returns:
        Merged dictionary
    """
    result = copy.deepcopy(base)

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)

    return result


def _require(config: Dict[str, Any], path: str, message: str) -> None:
    parts = path.split(".")
    cur: Any = config
    for part in parts:
        if not isinstance(cur, dict) or part not in cur or cur[part] in (None, ""):
            raise ValueError(message)
        cur = cur[part]


def _validate_params(backend: str, section: str, function_name: str, params: Dict[str, Any]) -> None:
    """Validate parameters against expected schema."""
    schemas = _get_param_schemas()

    if backend not in schemas:
        raise ValueError(f"Unknown backend: {backend}")

    if section not in schemas[backend]:
        raise ValueError(f"Unknown section: {section} for backend {backend}")

    if function_name not in schemas[backend][section]:
        raise ValueError(f"Unknown function: {function_name} for {backend}.{section}")

    expected_params = schemas[backend][section][function_name]
    provided_params = set(params.keys())

    # Check for unexpected parameters
    extra_params = provided_params - expected_params
    if extra_params:
        raise ValueError(
            f"Unexpected parameters for {backend}.{section}.{function_name}: "
            f"{sorted(extra_params)}. Expected: {sorted(expected_params)}"
        )

    # Check for missing required parameters (after defaults merge)
    missing_params = expected_params - provided_params
    if missing_params:
        raise ValueError(
            f"Missing required parameters for {backend}.{section}.{function_name}: {sorted(missing_params)}"
        )

    # Check for null values that must be user-provided (only for specific params)
    required_non_null_params = {"training_data_path"}  # Only these cannot be null
    for param, value in params.items():
        if value is None and param in required_non_null_params:
            raise ValueError(
                f"Parameter '{param}' for {backend}.{section}.{function_name} must be provided by user (cannot be null)"
            )


def validate_config(config: Dict[str, Any]) -> None:
    """Validate configuration has required fields and valid parameters."""

    # STORAGE is optional - if present, PATH is required
    if "STORAGE" in config:
        _require(
            config,
            "STORAGE.PATH",
            "Configuration with STORAGE must include STORAGE.PATH",
        )

    # Validate that exactly one of RULE or SYNTHESIZER is present
    has_rule = "RULE" in config
    has_synthesizer = "SYNTHESIZER" in config

    if has_rule and has_synthesizer:
        raise ValueError("Config must contain exactly one of RULE or SYNTHESIZER block, not both")
    elif not has_rule and not has_synthesizer:
        raise ValueError("Config must contain either RULE or SYNTHESIZER block")

    # Validate RULE backend
    if has_rule:
        rule_config = config["RULE"]

        # Validate CHARACTERISTICS
        if "CHARACTERISTICS" in rule_config:
            char_config = rule_config["CHARACTERISTICS"]
            function_name = char_config.get("FUNCTION", "default")
            params = char_config.get("PARAMS", {})
            _validate_params("RULE", "CHARACTERISTICS", function_name, params)

        # Validate METRICS
        if "METRICS" in rule_config:
            metrics_config = rule_config["METRICS"]
            function_name = metrics_config.get("FUNCTION", "default")
            params = metrics_config.get("PARAMS", {})
            _validate_params("RULE", "METRICS", function_name, params)

    # Validate SYNTHESIZER backend
    if has_synthesizer:
        syn_config = config["SYNTHESIZER"]

        # Validate CHARACTERISTICS
        if "CHARACTERISTICS" in syn_config:
            char_config = syn_config["CHARACTERISTICS"]
            function_name = char_config.get("FUNCTION")
            if not function_name:
                raise ValueError("SYNTHESIZER.CHARACTERISTICS.FUNCTION is required")
            params = char_config.get("PARAMS", {})
            _validate_params("SYNTHESIZER", "CHARACTERISTICS", function_name, params)

        # Validate METRICS
        if "METRICS" in syn_config:
            metrics_config = syn_config["METRICS"]
            function_name = metrics_config.get("FUNCTION")
            if not function_name:
                raise ValueError("SYNTHESIZER.METRICS.FUNCTION is required")
            params = metrics_config.get("PARAMS", {})
            _validate_params("SYNTHESIZER", "METRICS", function_name, params)


def process_config(config_path: str) -> Dict[str, Any]:
    """
    Load, merge with defaults, and validate configuration.

    Args:
        config_path: Path to user configuration file

    Returns:
        Complete validated configuration

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If configuration is invalid
    """
    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    # Load user config - support both YAML and JSON for backward compatibility
    with open(config_file, "r") as f:
        if config_file.suffix.lower() in [".yaml", ".yml"]:
            user_config = yaml.safe_load(f)
        else:
            user_config = json.load(f)

    # Load defaults
    defaults = load_defaults()

    # Remove conflicting blocks from defaults based on user config
    # User config determines which backend to use
    if "SYNTHESIZER" in user_config:
        # User wants SYNTHESIZER, remove RULE from defaults
        if "RULE" in defaults:
            defaults = copy.deepcopy(defaults)
            del defaults["RULE"]
    elif "RULE" in user_config:
        # User wants RULE, remove SYNTHESIZER from defaults
        if "SYNTHESIZER" in defaults:
            defaults = copy.deepcopy(defaults)
            del defaults["SYNTHESIZER"]
    else:
        # User didn't specify backend, default to RULE
        if "SYNTHESIZER" in defaults:
            defaults = copy.deepcopy(defaults)
            del defaults["SYNTHESIZER"]

    # Merge user config over defaults
    config = deep_merge(defaults, user_config)

    validate_config(config)
    return config
