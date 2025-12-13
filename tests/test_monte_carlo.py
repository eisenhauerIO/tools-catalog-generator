"""Tests for Monte Carlo sampling with SDV."""

import json
import pytest
from pathlib import Path
import tempfile
import shutil

from online_retail_simulator import simulate, train_synthesizer, generate_sample
from online_retail_simulator.monte_carlo_sampler import (
    check_sdv_available,
    validate_sdv_config,
    validate_sdv_config_for_generation,
    SDV_AVAILABLE,
)


@pytest.fixture
def temp_output_dir():
    """Create temporary output directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def monte_carlo_config(temp_output_dir):
    """Create test configuration for Monte Carlo sampling."""
    config = {
        "SEED": 42,
        "OUTPUT_DIR": temp_output_dir,
        "BASELINE": {
            "NUM_PRODUCTS": 10,
            "DATE_START": "2024-01-01",
            "DATE_END": "2024-01-05",
            "PRODUCTS_FILE": "products.json",
            "SALES_FILE": "sales.json"
        },
        "SDV": {
            "SYNTHESIZER_TYPE": "gaussian_copula",
            "MODEL_SALES_FILE": "synthesizer_sales.pkl",
            "MODEL_PRODUCTS_FILE": "synthesizer_products.pkl",
            "OUTPUT_PRODUCTS_FILE": "mc_products.json",
            "OUTPUT_SALES_FILE": "mc_sales.json"
        }
    }
    
    # Write config to temporary file
    config_path = Path(temp_output_dir) / "config_mc_test.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    return str(config_path)


class TestSDVAvailability:
    """Test SDV dependency availability."""
    
    def test_sdv_check(self):
        """Test that SDV availability check works."""
        if SDV_AVAILABLE:
            # Should not raise if SDV is available
            check_sdv_available()
        else:
            # Should raise ImportError if SDV not available
            with pytest.raises(ImportError, match="SDV dependencies not available"):
                check_sdv_available()


class TestConfigValidation:
    """Test configuration validation for SDV."""
    
    def test_validate_sdv_config_valid(self, monte_carlo_config, temp_output_dir):
        """Test validation passes for valid SDV config."""
        with open(monte_carlo_config, 'r') as f:
            config = json.load(f)
        
        # Should not raise
        validate_sdv_config(config)
    
    def test_validate_sdv_config_missing_section(self):
        """Test validation fails when SDV section is missing."""
        config = {"BASELINE": {}}
        
        with pytest.raises(ValueError, match="Configuration must include SDV section"):
            validate_sdv_config(config)
    
    def test_validate_sdv_config_missing_fields(self):
        """Test validation fails when required fields are missing."""
        config = {"SDV": {}}
        
        with pytest.raises(ValueError, match="SDV.MODEL_PRODUCTS_FILE is required"):
            validate_sdv_config(config)


@pytest.mark.skipif(not SDV_AVAILABLE, reason="SDV dependencies not installed")
class TestMonteCarloWorkflow:
    """Test full Monte Carlo sampling workflow."""
    
    def test_full_workflow(self, monte_carlo_config, temp_output_dir):
        """Test complete workflow: simulate -> train -> generate."""
        # Step 1: Generate baseline data
        products_df, sales_df = simulate(monte_carlo_config)
        
        # Check baseline files exist
        products_file = Path(temp_output_dir) / "products.json"
        sales_file = Path(temp_output_dir) / "sales.json"
        assert products_file.exists()
        assert sales_file.exists()
        
        # Load and verify baseline data
        with open(products_file, 'r') as f:
            products = json.load(f)
        with open(sales_file, 'r') as f:
            sales = json.load(f)
        
        assert len(products) == 10
        assert len(sales) > 0
        
        # Verify DataFrames were returned
        assert len(products_df) == 10
        assert len(sales_df) == len(sales)
        
        # Step 2: Train synthesizers with returned DataFrames
        train_synthesizer(monte_carlo_config, products_df=products_df, sales_df=sales_df)
        
        # Check model files exist
        model_products = Path(temp_output_dir) / "synthesizer_products.pkl"
        model_sales = Path(temp_output_dir) / "synthesizer_sales.pkl"
        assert model_products.exists()
        assert model_sales.exists()
        
        # Step 3: Generate Monte Carlo sample
        synthetic_products_df, synthetic_sales_df = generate_sample(monte_carlo_config)
        
        # Check output files exist
        mc_products = Path(temp_output_dir) / "mc_products.json"
        mc_sales = Path(temp_output_dir) / "mc_sales.json"
        assert mc_products.exists()
        assert mc_sales.exists()
        
        # Load and verify synthetic data
        with open(mc_products, 'r') as f:
            synthetic_products = json.load(f)
        with open(mc_sales, 'r') as f:
            synthetic_sales = json.load(f)
        
        # Check same size as training data
        assert len(synthetic_products) == len(products)
        assert len(synthetic_sales) == len(sales)
        
        # Verify returned DataFrames match files
        assert len(synthetic_products_df) == len(synthetic_products)
        assert len(synthetic_sales_df) == len(synthetic_sales)
        
        # Check data structure
        assert "product_id" in synthetic_products[0]
        assert "category" in synthetic_products[0]
        assert "price" in synthetic_products[0]
        
        assert "transaction_id" in synthetic_sales[0]
        assert "product_id" in synthetic_sales[0]
        assert "quantity" in synthetic_sales[0]
        assert "revenue" in synthetic_sales[0]
    
    def test_train_without_data(self, monte_carlo_config, temp_output_dir):
        """Test that training fails if DataFrames are not provided."""
        with pytest.raises(ValueError, match="products_df and sales_df must be provided"):
            train_synthesizer(monte_carlo_config)
    
    def test_generate_without_models(self, monte_carlo_config, temp_output_dir):
        """Test that generation fails if models don't exist."""
        # Generate baseline data but don't train
        products_df, sales_df = simulate(monte_carlo_config)
        
        with pytest.raises(FileNotFoundError, match="Products model not found"):
            generate_sample(monte_carlo_config)
    
    def test_multiple_samples(self, monte_carlo_config, temp_output_dir):
        """Test generating multiple Monte Carlo samples."""
        # Generate baseline and train
        products_df, sales_df = simulate(monte_carlo_config)
        train_synthesizer(monte_carlo_config, products_df=products_df, sales_df=sales_df)
        
        # Load config to modify output files
        with open(monte_carlo_config, 'r') as f:
            config = json.load(f)
        
        # Generate 3 samples with different output names
        for i in range(1, 4):
            config["SDV"]["OUTPUT_PRODUCTS_FILE"] = f"mc_sample_{i:03d}_products.json"
            config["SDV"]["OUTPUT_SALES_FILE"] = f"mc_sample_{i:03d}_sales.json"
            
            # Write updated config
            with open(monte_carlo_config, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Generate sample
            synthetic_products_df, synthetic_sales_df = generate_sample(monte_carlo_config)
            
            # Verify files exist
            mc_products = Path(temp_output_dir) / f"mc_sample_{i:03d}_products.json"
            mc_sales = Path(temp_output_dir) / f"mc_sample_{i:03d}_sales.json"
            assert mc_products.exists()
            assert mc_sales.exists()
            
            # Verify DataFrames are returned
            assert len(synthetic_products_df) > 0
            assert len(synthetic_sales_df) > 0
        
        # Verify all 3 samples exist
        sample_files = list(Path(temp_output_dir).glob("mc_sample_*"))
        assert len(sample_files) == 6  # 3 products + 3 sales files


@pytest.mark.skipif(not SDV_AVAILABLE, reason="SDV dependencies not installed")
class TestSynthesizerTypes:
    """Test different synthesizer types."""
    
    def test_gaussian_copula(self, monte_carlo_config, temp_output_dir):
        """Test Gaussian Copula synthesizer."""
        products_df, sales_df = simulate(monte_carlo_config)
        train_synthesizer(monte_carlo_config, products_df=products_df, sales_df=sales_df)
        synthetic_products_df, synthetic_sales_df = generate_sample(monte_carlo_config)
        
        mc_products = Path(temp_output_dir) / "mc_products.json"
        assert mc_products.exists()
        assert len(synthetic_products_df) > 0
    
    @pytest.mark.slow
    def test_ctgan(self, monte_carlo_config, temp_output_dir):
        """Test CTGAN synthesizer (slower, neural network)."""
        # Update config to use CTGAN
        with open(monte_carlo_config, 'r') as f:
            config = json.load(f)
        config["SDV"]["SYNTHESIZER_TYPE"] = "ctgan"
        with open(monte_carlo_config, 'w') as f:
            json.dump(config, f, indent=2)
        
        products_df, sales_df = simulate(monte_carlo_config)
        train_synthesizer(monte_carlo_config, products_df=products_df, sales_df=sales_df)
        synthetic_products_df, synthetic_sales_df = generate_sample(monte_carlo_config)
        
        mc_products = Path(temp_output_dir) / "mc_products.json"
        assert mc_products.exists()
        assert len(synthetic_products_df) > 0
    
    def test_invalid_synthesizer(self, monte_carlo_config, temp_output_dir):
        """Test that invalid synthesizer type raises error."""
        # Update config with invalid synthesizer
        with open(monte_carlo_config, 'r') as f:
            config = json.load(f)
        config["SDV"]["SYNTHESIZER_TYPE"] = "invalid_type"
        with open(monte_carlo_config, 'w') as f:
            json.dump(config, f, indent=2)
        
        products_df, sales_df = simulate(monte_carlo_config)
        
        with pytest.raises(ValueError, match="Unknown synthesizer type"):
            train_synthesizer(monte_carlo_config, products_df=products_df, sales_df=sales_df)
