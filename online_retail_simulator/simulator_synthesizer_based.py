"""SDV-based synthesizer training and sampling for synthetic retail data."""

import json
import pickle
from pathlib import Path
from typing import Optional, Tuple, Dict

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
    sales_df: Optional[pd.DataFrame] = None,
    config: Optional[Dict] = None
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
    if config is None:
        with open(config_path, 'r') as f:
            config = json.load(f)
    _validate_sdv_config(config)
    
    syn_config = config["SYNTHESIZER"]
    synthesizer_type = syn_config.get("SYNTHESIZER_TYPE", "gaussian_copula")
    output_dir = config.get("OUTPUT", {}).get("dir", config.get("OUTPUT_DIR", "output"))
    prefix = config.get("OUTPUT", {}).get("file_prefix", "run")
    products_model_file = f"{prefix}_model_products.pkl"
    sales_model_file = f"{prefix}_model_sales.pkl"
    
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
    df: pd.DataFrame,
    num_rows: int,
    synthesizer_type: str = "gaussian_copula"
) -> pd.DataFrame:
    """
    Generate synthetic data using an SDV synthesizer trained on a single DataFrame.

    Args:
        df: Input DataFrame (already merged with all required info)
        num_rows: Number of synthetic rows to generate
        synthesizer_type: Type of SDV synthesizer ("gaussian_copula", "ctgan", "tvae")

    Returns:
        Synthetic DataFrame of shape (num_rows, df.shape[1])

    Raises:
        ValueError: If num_rows is not positive
    """
    _check_sdv_available()
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    if not isinstance(num_rows, int) or num_rows <= 0:
        raise ValueError("num_rows must be a positive integer")

    print("=" * 60)
    print("Training SDV Synthesizer (single-table)")
    print("=" * 60)
    print(f"Synthesizer Type: {synthesizer_type}")
    print(f"Input Data: {len(df)} rows, {df.shape[1]} columns")

    synthesizer_class = _get_synthesizer_class(synthesizer_type)
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(df)
    synthesizer = synthesizer_class(metadata=metadata)
    synthesizer.fit(df)

    print(f"\nGenerating {num_rows} synthetic rows...")
    synthetic_df = synthesizer.sample(num_rows=num_rows)
    print(f"✓ Generated {len(synthetic_df)} synthetic rows")
    print("\n✓ Sampling complete!")
    return synthetic_df


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



def _resolve_model_paths(
    output_dir: Path,
    preferred_prefix: str,
    preferred_products_name: str,
    preferred_sales_name: str
) -> Tuple[Path, Path, str]:
    """Resolve trained model file paths, with a fallback to existing pairs.

    If models for the preferred prefix are missing, search the output directory for
    any matching products/sales model pair. This supports workflows where the
    output prefix is changed between training and sampling.
    """
    preferred_products = output_dir / preferred_products_name
    preferred_sales = output_dir / preferred_sales_name

    if preferred_products.exists() and preferred_sales.exists():
        return preferred_products, preferred_sales, preferred_prefix

    # Attempt to find a single existing model pair as a fallback
    product_models = list(output_dir.glob("*_model_products.pkl"))
    sales_models = {
        p.stem.replace("_model_sales", ""): p
        for p in output_dir.glob("*_model_sales.pkl")
    }

    matches = []
    for product_file in product_models:
        prefix = product_file.stem.replace("_model_products", "")
        sales_file = sales_models.get(prefix)
        if sales_file:
            matches.append((prefix, product_file, sales_file))

    if len(matches) == 1:
        prefix, product_file, sales_file = matches[0]
        return product_file, sales_file, prefix

    if not preferred_products.exists():
        raise FileNotFoundError(f"Products model not found: {preferred_products}")
    raise FileNotFoundError(f"Sales model not found: {preferred_sales}")


def _validate_sdv_config(config: dict) -> None:
    """Validate synthesizer configuration section."""
    _check_sdv_available()
    if "SYNTHESIZER" not in config:
        raise ValueError("Configuration must include 'SYNTHESIZER' section")
    syn_config = config["SYNTHESIZER"]
    if "SYNTHESIZER_TYPE" not in syn_config:
        raise ValueError("SYNTHESIZER config must include 'SYNTHESIZER_TYPE'")
