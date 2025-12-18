"""Configuration processing with defaults and validation."""

import copy
import json
from pathlib import Path
from typing import Any, Dict

import yaml


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


def validate_config(config: Dict[str, Any]) -> None:
    """Validate configuration has required fields for the selected simulator."""

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

    # Validate SYNTHESIZER-specific requirements
    if has_synthesizer:
        syn = config["SYNTHESIZER"]
        _require(
            {"SYNTHESIZER": syn},
            "SYNTHESIZER.CHARACTERISTICS",
            "SYNTHESIZER.CHARACTERISTICS is required",
        )
        _require(
            {"SYNTHESIZER": syn},
            "SYNTHESIZER.CHARACTERISTICS.FUNCTION",
            "SYNTHESIZER.CHARACTERISTICS.FUNCTION is required",
        )
        _require(
            {"SYNTHESIZER": syn},
            "SYNTHESIZER.CHARACTERISTICS.PARAMS",
            "SYNTHESIZER.CHARACTERISTICS.PARAMS is required",
        )
        _require(
            {"SYNTHESIZER": syn},
            "SYNTHESIZER.METRICS",
            "SYNTHESIZER.METRICS is required",
        )
        _require(
            {"SYNTHESIZER": syn},
            "SYNTHESIZER.METRICS.FUNCTION",
            "SYNTHESIZER.METRICS.FUNCTION is required",
        )
        _require(
            {"SYNTHESIZER": syn},
            "SYNTHESIZER.METRICS.PARAMS",
            "SYNTHESIZER.METRICS.PARAMS is required",
        )


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
    if "SYNTHESIZER" in user_config and "RULE" in defaults:
        defaults = copy.deepcopy(defaults)
        del defaults["RULE"]
    elif "RULE" in user_config and "SYNTHESIZER" in defaults:
        defaults = copy.deepcopy(defaults)
        del defaults["SYNTHESIZER"]

    # Merge user config over defaults
    config = deep_merge(defaults, user_config)

    validate_config(config)
    return config
