"""SDV-based synthesizer training and sampling for synthetic retail data."""

import json
import pickle
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd

try:
    from sdv.single_table import GaussianCopulaSynthesizer, CTGANSynthesizer, TVAESynthesizer
    from sdv.metadata import SingleTableMetadata
    _SDV_AVAILABLE = True
except ImportError:
    _SDV_AVAILABLE = False


def train_synthesizer(
    config_path: str,
    products_df: Optional[pd.DataFrame] = None,
    sales_df: Optional[pd.DataFrame] = None
) -> None:
    """
    Train SDV synthesizers on provided product and sales data.
    
    Args:
        config_path: Path to JSON configuration file
        products_df: DataFrame of products (required; no fallback)
        sales_df: DataFrame of sales (required; no fallback)
    
    Raises:
        TypeError: If products_df or sales_df is not provided or not a DataFrame
        ValueError: If config is invalid
    """
    if products_df is None or not isinstance(products_df, pd.DataFrame):
        raise TypeError("train_synthesizer requires products_df as a pandas DataFrame")
    if sales_df is None or not isinstance(sales_df, pd.DataFrame):
        raise TypeError("train_synthesizer requires sales_df as a pandas DataFrame")
    
    _check_sdv_available()
    
    # Load and validate config
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    _validate_sdv_config(config)
    
    sdv_config = config["SDV"]
    synthesizer_type = sdv_config.get("SYNTHESIZER_TYPE", "gaussian_copula")
    output_dir = config.get("OUTPUT_DIR", "output")
    products_model_file = sdv_config.get("MODEL_PRODUCTS_FILE", "synthesizer_products.pkl")
    sales_model_file = sdv_config.get("MODEL_SALES_FILE", "synthesizer_sales.pkl")
    
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("Training SDV Synthesizers")
    print("=" * 60)
    print(f"Synthesizer Type: {synthesizer_type}")
    print(f"Products Data: {len(products_df)} rows")
    print(f"Sales Data: {len(sales_df)} rows")
    
    # Get synthesizer class
    synthesizer_class = _get_synthesizer_class(synthesizer_type)
    
    # Train products synthesizer
    print(f"\nTraining {synthesizer_type} on products...")
    products_metadata = SingleTableMetadata()
    products_metadata.detect_from_dataframe(products_df)
    products_synthesizer = synthesizer_class(metadata=products_metadata)
    products_synthesizer.fit(products_df)
    products_model_path = f"{output_dir}/{products_model_file}"
    with open(products_model_path, 'wb') as f:
        pickle.dump(products_synthesizer, f)
    print(f"✓ Saved products model to {products_model_path}")
    
    # Train sales synthesizer
    print(f"Training {synthesizer_type} on sales...")
    sales_metadata = SingleTableMetadata()
    sales_metadata.detect_from_dataframe(sales_df)
    sales_synthesizer = synthesizer_class(metadata=sales_metadata)
    sales_synthesizer.fit(sales_df)
    sales_model_path = f"{output_dir}/{sales_model_file}"
    with open(sales_model_path, 'wb') as f:
        pickle.dump(sales_synthesizer, f)
    print(f"✓ Saved sales model to {sales_model_path}")
    
    print("\n✓ Training complete!")


def simulate_synthesizer_based(
    config_path: str,
    num_rows_products: Optional[int] = None,
    num_rows_sales: Optional[int] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate synthetic data using trained SDV synthesizers.
    
    Args:
        config_path: Path to JSON configuration file
        num_rows_products: Number of synthetic products to generate
                          (uses DEFAULT_PRODUCTS_ROWS from config if not provided)
        num_rows_sales: Number of synthetic sales to generate
                       (uses DEFAULT_SALES_ROWS from config if not provided)
    
    Returns:
        Tuple of (products_df, sales_df) as pandas DataFrames
    
    Raises:
        ValueError: If row counts cannot be determined
        FileNotFoundError: If trained model files do not exist
    """
    _check_sdv_available()
    
    # Load config
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    _validate_sdv_config(config)
    
    sdv_config = config["SDV"]
    output_dir = config.get("OUTPUT_DIR", "output")
    products_model_file = sdv_config.get("MODEL_PRODUCTS_FILE", "synthesizer_products.pkl")
    sales_model_file = sdv_config.get("MODEL_SALES_FILE", "synthesizer_sales.pkl")
    products_output_file = sdv_config.get("OUTPUT_PRODUCTS_FILE", "mc_products.json")
    sales_output_file = sdv_config.get("OUTPUT_SALES_FILE", "mc_sales.json")
    
    # Determine row counts
    if num_rows_products is None:
        num_rows_products = sdv_config.get("DEFAULT_PRODUCTS_ROWS")
    if num_rows_sales is None:
        num_rows_sales = sdv_config.get("DEFAULT_SALES_ROWS")
    
    if num_rows_products is None or num_rows_sales is None:
        raise ValueError(
            "Row counts must be provided as arguments or in config as "
            "DEFAULT_PRODUCTS_ROWS and DEFAULT_SALES_ROWS"
        )
    
    # Check model files exist
    products_model_path = f"{output_dir}/{products_model_file}"
    sales_model_path = f"{output_dir}/{sales_model_file}"
    
    if not Path(products_model_path).exists():
        raise FileNotFoundError(f"Products model not found: {products_model_path}")
    if not Path(sales_model_path).exists():
        raise FileNotFoundError(f"Sales model not found: {sales_model_path}")
    
    # Load models
    with open(products_model_path, 'rb') as f:
        products_synthesizer = pickle.load(f)
    with open(sales_model_path, 'rb') as f:
        sales_synthesizer = pickle.load(f)
    
    print("=" * 60)
    print("Generating Synthetic Data")
    print("=" * 60)
    print(f"Products: {num_rows_products} rows")
    print(f"Sales: {num_rows_sales} rows")
    
    # Generate synthetic data
    print("\nGenerating synthetic products...")
    products_df = products_synthesizer.sample(num_rows=num_rows_products)
    print(f"✓ Generated {len(products_df)} products")
    
    print("Generating synthetic sales...")
    sales_df = sales_synthesizer.sample(num_rows=num_rows_sales)
    print(f"✓ Generated {len(sales_df)} sales")
    
    # Save synthetic data to JSON
    print(f"\nSaving synthetic data to {output_dir}/...")
    products_output_path = f"{output_dir}/{products_output_file}"
    sales_output_path = f"{output_dir}/{sales_output_file}"
    
    with open(products_output_path, 'w') as f:
        json.dump(products_df.to_dict(orient='records'), f, indent=2, default=str)
    print(f"Data saved to {products_output_path}")
    
    with open(sales_output_path, 'w') as f:
        json.dump(sales_df.to_dict(orient='records'), f, indent=2, default=str)
    print(f"Data saved to {sales_output_path}")
    
    print("\n✓ Sampling complete!")
    
    return products_df, sales_df


# ============================================================================
# Private Section: Helpers
# ============================================================================

def _check_sdv_available() -> None:
    """Check if SDV is installed; raise ImportError if not."""
    if not _SDV_AVAILABLE:
        raise ImportError(
            "SDV is required for synthesizer-based simulation. "
            "Install it with: pip install sdv"
        )


def _get_synthesizer_class(synthesizer_type: str):
    """Get synthesizer class by name."""
    _check_sdv_available()
    
    synthesizer_map = {
        "gaussian_copula": GaussianCopulaSynthesizer,
        "ctgan": CTGANSynthesizer,
        "tvae": TVAESynthesizer,
    }
    
    if synthesizer_type not in synthesizer_map:
        raise ValueError(
            f"Unknown synthesizer type: {synthesizer_type}. "
            f"Supported: {list(synthesizer_map.keys())}"
        )
    
    return synthesizer_map[synthesizer_type]


def _validate_sdv_config(config: dict) -> None:
    """Validate SDV configuration section."""
    _check_sdv_available()
    
    if "SDV" not in config:
        raise ValueError("Configuration must include 'SDV' section")
    
    sdv_config = config["SDV"]
    required_fields = ["SYNTHESIZER_TYPE", "MODEL_PRODUCTS_FILE", "MODEL_SALES_FILE"]
    for field in required_fields:
        if field not in sdv_config:
            raise ValueError(f"SDV config must include '{field}'")
