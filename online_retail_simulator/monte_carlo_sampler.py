"""Monte Carlo sampling using SDV for synthetic data generation."""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

try:
    import pandas as pd
    from sdv.metadata import Metadata
    from sdv.single_table import GaussianCopulaSynthesizer, CTGANSynthesizer, TVAESynthesizer
    SDV_AVAILABLE = True
except ImportError:
    SDV_AVAILABLE = False

from .config_processor import process_config


def check_sdv_available():
    """Check if SDV dependencies are available."""
    if not SDV_AVAILABLE:
        raise ImportError(
            "SDV dependencies not available. Install with: pip install sdv pandas"
        )


def load_json_to_dataframe(filepath: str) -> pd.DataFrame:
    """
    Load JSON data to pandas DataFrame.
    
    Args:
        filepath: Path to JSON file
    
    Returns:
        DataFrame with loaded data
    """
    check_sdv_available()
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    return pd.DataFrame(data)


def get_synthesizer_class(synthesizer_type: str):
    """
    Get SDV synthesizer class by type.
    
    Args:
        synthesizer_type: Type of synthesizer ("gaussian_copula", "ctgan", or "tvae")
    
    Returns:
        Synthesizer class
    """
    synthesizer_map = {
        "gaussian_copula": GaussianCopulaSynthesizer,
        "ctgan": CTGANSynthesizer,
        "tvae": TVAESynthesizer,
    }
    
    if synthesizer_type not in synthesizer_map:
        raise ValueError(
            f"Unknown synthesizer type: {synthesizer_type}. "
            f"Choose from: {', '.join(synthesizer_map.keys())}"
        )
    
    return synthesizer_map[synthesizer_type]


def train_synthesizer(
    config_path: str,
    products_df: Optional[pd.DataFrame] = None,
    sales_df: Optional[pd.DataFrame] = None
) -> None:
    """
    Train SDV synthesizers on products and sales data.
    
    Args:
        config_path: Path to JSON configuration file
        products_df: Products DataFrame. Required - cannot load from file.
        sales_df: Sales DataFrame. Required - cannot load from file.
        
    Raises:
        ValueError: If DataFrames are not provided
    """
    check_sdv_available()
    
    # Validate that DataFrames are provided
    if products_df is None or sales_df is None:
        raise ValueError(
            "products_df and sales_df must be provided. "
            "File-based loading is no longer supported."
        )
    
    # Load and validate config
    config = process_config(config_path)
    validate_sdv_config(config)
    
    output_dir = config.get("OUTPUT_DIR", "output")
    sdv_config = config["SDV"]
    
    # Get file paths for models
    model_products_file = f"{output_dir}/{sdv_config['MODEL_PRODUCTS_FILE']}"
    model_sales_file = f"{output_dir}/{sdv_config['MODEL_SALES_FILE']}"
    synthesizer_type = sdv_config.get("SYNTHESIZER_TYPE", "gaussian_copula")
    
    print("=" * 60)
    print("SDV Monte Carlo Sampler - Training")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  Synthesizer Type: {synthesizer_type}")
    print(f"  Products: {len(products_df)} rows")
    print(f"  Sales: {len(sales_df)} rows")
    
    # Get synthesizer class
    synthesizer_class = get_synthesizer_class(synthesizer_type)
    
    # Train products synthesizer
    print(f"\nTraining products synthesizer...")
    products_metadata = Metadata.detect_from_dataframe(products_df)
    products_synthesizer = synthesizer_class(products_metadata)
    products_synthesizer.fit(products_df)
    print(f"✓ Products synthesizer trained")
    
    # Train sales synthesizer
    print(f"\nTraining sales synthesizer...")
    sales_metadata = Metadata.detect_from_dataframe(sales_df)
    sales_synthesizer = synthesizer_class(sales_metadata)
    sales_synthesizer.fit(sales_df)
    print(f"✓ Sales synthesizer trained")
    
    # Save models
    print(f"\nSaving models to {output_dir}/...")
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    products_synthesizer.save(model_products_file)
    sales_synthesizer.save(model_sales_file)
    print(f"✓ Products model saved to {model_products_file}")
    print(f"✓ Sales model saved to {model_sales_file}")
    
    print(f"\n✓ Training complete!")


def generate_sample(config_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate a single Monte Carlo sample using trained synthesizers.
    
    Loads trained synthesizer models and generates synthetic products
    and sales data with the same number of rows as the training data.
    Saves output to separate files and returns DataFrames.
    
    Args:
        config_path: Path to JSON configuration file
        
    Returns:
        Tuple of (synthetic_products_df, synthetic_sales_df)
    """
    check_sdv_available()
    
    # Load config
    config = process_config(config_path)
    validate_sdv_config_for_generation(config)
    
    output_dir = config.get("OUTPUT_DIR", "output")
    sdv_config = config["SDV"]
    
    # Get file paths
    model_products_file = f"{output_dir}/{sdv_config['MODEL_PRODUCTS_FILE']}"
    model_sales_file = f"{output_dir}/{sdv_config['MODEL_SALES_FILE']}"
    output_products_file = f"{output_dir}/{sdv_config['OUTPUT_PRODUCTS_FILE']}"
    output_sales_file = f"{output_dir}/{sdv_config['OUTPUT_SALES_FILE']}"
    synthesizer_type = sdv_config.get("SYNTHESIZER_TYPE", "gaussian_copula")
    
    # Get baseline file paths for size matching
    products_source = f"{output_dir}/{sdv_config.get('INPUT_PRODUCTS_SOURCE', 'products.json')}"
    sales_source = f"{output_dir}/{sdv_config.get('INPUT_SALES_SOURCE', 'sales.json')}"
    
    # Validate model files exist
    if not Path(model_products_file).exists():
        raise FileNotFoundError(
            f"Products model not found: {model_products_file}. "
            f"Run train_synthesizer() first."
        )
    if not Path(model_sales_file).exists():
        raise FileNotFoundError(
            f"Sales model not found: {model_sales_file}. "
            f"Run train_synthesizer() first."
        )
    
    print("=" * 60)
    print("SDV Monte Carlo Sampler - Generating Sample")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  Synthesizer Type: {synthesizer_type}")
    print(f"  Output Products:  {output_products_file}")
    print(f"  Output Sales:     {output_sales_file}")
    
    # Load original data to get row counts
    print(f"\nLoading training data for size matching...")
    products_df_original = load_json_to_dataframe(products_source)
    sales_df_original = load_json_to_dataframe(sales_source)
    num_products = len(products_df_original)
    num_sales = len(sales_df_original)
    print(f"✓ Target size: {num_products} products, {num_sales} sales")
    
    # Load models
    print(f"\nLoading trained models...")
    synthesizer_class = get_synthesizer_class(synthesizer_type)
    products_synthesizer = synthesizer_class.load(model_products_file)
    sales_synthesizer = synthesizer_class.load(model_sales_file)
    print(f"✓ Models loaded")
    
    # Generate synthetic data
    print(f"\nGenerating synthetic data...")
    synthetic_products_df = products_synthesizer.sample(num_rows=num_products)
    synthetic_sales_df = sales_synthesizer.sample(num_rows=num_sales)
    print(f"✓ Generated {len(synthetic_products_df)} synthetic products")
    print(f"✓ Generated {len(synthetic_sales_df)} synthetic sales")
    
    # Convert to list of dicts and save
    print(f"\nSaving synthetic data to {output_dir}/...")
    synthetic_products = synthetic_products_df.to_dict(orient='records')
    synthetic_sales = synthetic_sales_df.to_dict(orient='records')
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    with open(output_products_file, 'w') as f:
        json.dump(synthetic_products, f, indent=2)
    
    with open(output_sales_file, 'w') as f:
        json.dump(synthetic_sales, f, indent=2)
    
    print(f"✓ Products saved to {output_products_file}")
    print(f"✓ Sales saved to {output_sales_file}")
    
    print(f"\n✓ Sample generation complete!")
    
    return synthetic_products_df, synthetic_sales_df


def validate_sdv_config(config: Dict[str, Any]) -> None:
    """
    Validate SDV configuration section for train_synthesizer().
    
    Args:
        config: Complete configuration dictionary
    
    Raises:
        ValueError: If SDV configuration is invalid or missing
    """
    if "SDV" not in config:
        raise ValueError("Configuration must include SDV section")
    
    sdv_config = config["SDV"]
    
    required_fields = [
        "MODEL_PRODUCTS_FILE",
        "MODEL_SALES_FILE",
        "OUTPUT_PRODUCTS_FILE",
        "OUTPUT_SALES_FILE",
    ]
    
    for field in required_fields:
        if field not in sdv_config or not sdv_config[field]:
            raise ValueError(f"SDV.{field} is required")


def validate_sdv_config_for_generation(config: Dict[str, Any]) -> None:
    """
    Validate SDV configuration section for generate_sample().
    
    Args:
        config: Complete configuration dictionary
    
    Raises:
        ValueError: If SDV configuration is invalid or missing
    """
    if "SDV" not in config:
        raise ValueError("Configuration must include SDV section")
    
    sdv_config = config["SDV"]
    
    required_fields = [
        "MODEL_PRODUCTS_FILE",
        "MODEL_SALES_FILE",
        "OUTPUT_PRODUCTS_FILE",
        "OUTPUT_SALES_FILE",
    ]
    
    for field in required_fields:
        if field not in sdv_config or not sdv_config[field]:
            raise ValueError(f"SDV.{field} is required")
