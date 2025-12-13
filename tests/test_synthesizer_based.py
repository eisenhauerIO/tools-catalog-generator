"""Tests for Monte Carlo sampling with SDV."""

import json
import pytest
from pathlib import Path
import tempfile
import shutil

from online_retail_simulator import simulate, train_synthesizer, simulate_synthesizer_based
from online_retail_simulator.simulator_synthesizer_based import (
    _check_sdv_available,
    _validate_sdv_config,
    _SDV_AVAILABLE,
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
        "SIMULATOR": {"mode": "synthesizer"},
        "SEED": 42,
        "OUTPUT": {"dir": temp_output_dir, "file_prefix": "mc"},
        "BASELINE": {
            "NUM_PRODUCTS": 10,
            "DATE_START": "2024-01-01",
            "DATE_END": "2024-01-05",
            "SALE_PROB": 0.7
        },
        "SYNTHESIZER": {
            "SYNTHESIZER_TYPE": "gaussian_copula",
            "DEFAULT_PRODUCTS_ROWS": 10,
            "DEFAULT_SALES_ROWS": 100
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
        if _SDV_AVAILABLE:
            # Should not raise if SDV is available
            _check_sdv_available()
        else:
            # Should raise ImportError if SDV not available
            with pytest.raises(ImportError, match="SDV dependencies not available"):
                _check_sdv_available()


class TestConfigValidation:
    """Test configuration validation for SDV."""
    
    def test_validate_sdv_config_valid(self, monte_carlo_config, temp_output_dir):
        """Test validation passes for valid SDV config."""
        with open(monte_carlo_config, 'r') as f:
            config = json.load(f)
        
        # Should not raise
        _validate_sdv_config(config)
    
    def test_validate_sdv_config_missing_section(self):
        """Test validation fails when SDV section is missing."""
        config = {"BASELINE": {}}
        
        with pytest.raises(ValueError, match="Configuration must include 'SYNTHESIZER' section"):
            _validate_sdv_config(config)
    
    def test_validate_sdv_config_missing_fields(self):
        """Test validation fails when required fields are missing."""
        config = {"SYNTHESIZER": {}}
        
        with pytest.raises(ValueError, match="SYNTHESIZER config must include"):
            _validate_sdv_config(config)


@pytest.mark.skipif(not _SDV_AVAILABLE, reason="SDV dependencies not installed")
class TestMonteCarloWorkflow:
    """Test full Monte Carlo sampling workflow."""
    
    def test_full_workflow(self, monte_carlo_config, temp_output_dir):
        """Test complete workflow: simulate -> synthesize."""
        # Step 1: Generate baseline data and merge
        products_df, sales_df = simulate(monte_carlo_config, mode="rule")
        merged_df = sales_df.merge(products_df, on="product_id", how="left")
        assert len(merged_df) == len(sales_df)

        # Step 2: Generate synthetic sample from merged data
        from online_retail_simulator.simulator_synthesizer_based import simulate_synthesizer_based
        synthetic_df = simulate_synthesizer_based(merged_df, num_rows=len(merged_df))
        assert isinstance(synthetic_df, type(merged_df))
        assert len(synthetic_df) == len(merged_df)
        # Check some expected columns
        expected_cols = ["product_id", "date", "quantity", "revenue", "name", "category", "price"]
        for col in expected_cols:
            assert col in synthetic_df.columns
    
    def test_train_without_data(self, monte_carlo_config, temp_output_dir):
        """Test that training fails if DataFrames are not provided."""
        with pytest.raises(TypeError):
            # Missing required positional DataFrame args
            train_synthesizer(monte_carlo_config)  # type: ignore
    
    
    def test_multiple_samples(self, monte_carlo_config, temp_output_dir):
        """Test generating multiple Monte Carlo samples with new interface."""
        products_df, sales_df = simulate(monte_carlo_config, mode="rule")
        merged_df = sales_df.merge(products_df, on="product_id", how="left")
        from online_retail_simulator.simulator_synthesizer_based import simulate_synthesizer_based
        samples = []
        for i in range(3):
            synthetic_df = simulate_synthesizer_based(merged_df, num_rows=len(merged_df))
            assert isinstance(synthetic_df, type(merged_df))
            assert len(synthetic_df) == len(merged_df)
            samples.append(synthetic_df)


@pytest.mark.skipif(not _SDV_AVAILABLE, reason="SDV dependencies not installed")
class TestSynthesizerTypes:
    """Test different synthesizer types."""
    
    def test_gaussian_copula(self, monte_carlo_config, temp_output_dir):
        """Test Gaussian Copula synthesizer (new interface)."""
        products_df, sales_df = simulate(monte_carlo_config, mode="rule")
        merged_df = sales_df.merge(products_df, on="product_id", how="left")
        from online_retail_simulator.simulator_synthesizer_based import simulate_synthesizer_based
        synthetic_df = simulate_synthesizer_based(merged_df, num_rows=len(merged_df), synthesizer_type="gaussian_copula")
        assert isinstance(synthetic_df, type(merged_df))
        assert len(synthetic_df) == len(merged_df)
    
    @pytest.mark.slow
    def test_ctgan(self, monte_carlo_config, temp_output_dir):
        """Test CTGAN synthesizer (new interface, slower, neural network)."""
        products_df, sales_df = simulate(monte_carlo_config, mode="rule")
        merged_df = sales_df.merge(products_df, on="product_id", how="left")
        from online_retail_simulator.simulator_synthesizer_based import simulate_synthesizer_based
        synthetic_df = simulate_synthesizer_based(merged_df, num_rows=len(merged_df), synthesizer_type="ctgan")
        assert isinstance(synthetic_df, type(merged_df))
        assert len(synthetic_df) == len(merged_df)
    
    def test_invalid_synthesizer(self, monte_carlo_config, temp_output_dir):
        """Test that invalid synthesizer type raises error."""
        # Update config with invalid synthesizer
        with open(monte_carlo_config, 'r') as f:
            config = json.load(f)
        config["SYNTHESIZER"]["SYNTHESIZER_TYPE"] = "invalid_type"
        with open(monte_carlo_config, 'w') as f:
            json.dump(config, f, indent=2)
        
        products_df, sales_df = simulate(monte_carlo_config, mode="rule")
        
        with pytest.raises(ValueError, match="Unknown synthesizer type"):
            train_synthesizer(monte_carlo_config, products_df=products_df, sales_df=sales_df)
