"""Configuration processing with defaults and validation."""

import json
from pathlib import Path
from typing import Dict, Any
import copy


def load_defaults() -> Dict[str, Any]:
    """Load default configuration from package."""
    defaults_path = Path(__file__).parent / "config_defaults.json"
    with open(defaults_path, 'r') as f:
        return json.load(f)


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


def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate configuration has required fields.
    
    Args:
        config: Configuration dictionary
    
    Raises:
        ValueError: If required fields are missing
    """
    # Check for BASELINE section
    if "BASELINE" not in config:
        raise ValueError("Configuration must include BASELINE section")
    
    baseline = config["BASELINE"]
    
    # Required fields in BASELINE
    if "DATE_START" not in baseline or not baseline["DATE_START"]:
        raise ValueError("BASELINE.DATE_START is required")
    
    if "DATE_END" not in baseline or not baseline["DATE_END"]:
        raise ValueError("BASELINE.DATE_END is required")
    
    # If ENRICHMENT section exists and has START_DATE, validate it
    if "ENRICHMENT" in config:
        enrichment = config["ENRICHMENT"]
        
        # Only validate if START_DATE is provided (not empty string)
        if "START_DATE" in enrichment and enrichment["START_DATE"]:
            # Validate enrichment start is within baseline date range
            if enrichment["START_DATE"] < baseline["DATE_START"]:
                raise ValueError("ENRICHMENT.START_DATE must be >= BASELINE.DATE_START")
            
            if enrichment["START_DATE"] > baseline["DATE_END"]:
                raise ValueError("ENRICHMENT.START_DATE must be <= BASELINE.DATE_END")


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
    
    # Load user config
    with open(config_file, 'r') as f:
        user_config = json.load(f)
    
    # Load defaults
    defaults = load_defaults()
    
    # Merge user config over defaults
    config = deep_merge(defaults, user_config)
    
    # Validate
    validate_config(config)
    
    return config
