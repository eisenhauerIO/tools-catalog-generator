"""Tests for Monte Carlo sampling with SDV."""

import json
import pytest
from .import_helpers import has_synthesizer
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


def monte_carlo_config(temp_output_dir, mode="synthesizer"):
    """Create test configuration for Monte Carlo sampling. Mode can be 'rule' or 'synthesizer'."""
    config = {
        "SIMULATOR": {"mode": mode},
        "SEED": 42,
        "OUTPUT": {"dir": temp_output_dir, "file_prefix": "mc"},
        "RULE": {
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
    config_path = Path(temp_output_dir) / f"config_mc_test_{mode}.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    return str(config_path)


@pytest.mark.skipif(not has_synthesizer(), reason="SDV dependencies not installed")
class TestSDVAvailability:
    """Test SDV dependency availability."""
    def test_sdv_check(self):
        """Test that SDV availability check works."""
        if _SDV_AVAILABLE:
            _check_sdv_available()
        else:
            with pytest.raises(ImportError, match="SDV is required for synthesizer-based simulation. Install it with: pip install sdv"):
                _check_sdv_available()


@pytest.mark.skipif(not has_synthesizer(), reason="SDV dependencies not installed")
class TestConfigValidation:
    """Test configuration validation for SDV."""
    def test_validate_sdv_config_valid(self, temp_output_dir):
        config_path = monte_carlo_config(temp_output_dir)
        with open(config_path, 'r') as f:
            config = json.load(f)
        _validate_sdv_config(config)
    def test_validate_sdv_config_missing_section(self):
        config = {"BASELINE": {}}
        with pytest.raises(ValueError, match="Configuration must include 'SYNTHESIZER' section"):
            _validate_sdv_config(config)
    def test_validate_sdv_config_missing_fields(self):
        config = {"SYNTHESIZER": {}}
        with pytest.raises(ValueError, match="SYNTHESIZER config must include"):
            _validate_sdv_config(config)


@pytest.mark.skipif(not has_synthesizer(), reason="SDV dependencies not installed")
class TestMonteCarloWorkflow:
    """Test full Monte Carlo sampling workflow."""
    
    def test_full_workflow(self, temp_output_dir):
        """Test complete workflow: simulate -> synthesize."""
        # Step 1: Generate baseline data and merge
        rule_config = monte_carlo_config(temp_output_dir, mode="rule")
        merged_df = simulate(rule_config)
        assert not merged_df.empty

        # Step 2: Generate synthetic sample from merged data
        synth_config = monte_carlo_config(temp_output_dir, mode="synthesizer")
        synthetic_df = simulate(synth_config, df=merged_df)
        assert isinstance(synthetic_df, type(merged_df))
        assert len(synthetic_df) == len(merged_df)
        # Check some expected columns
        expected_cols = ["product_id", "date", "quantity", "revenue", "name", "category", "price"]
        for col in expected_cols:
            assert col in synthetic_df.columns
    
    def test_train_without_data(self, temp_output_dir):
        """Test that training fails if DataFrames are not provided."""
        config_path = monte_carlo_config(temp_output_dir)
        with pytest.raises(TypeError):
            # Missing required positional DataFrame args
            train_synthesizer(config_path)  # type: ignore
    
    
    def test_multiple_samples(self, temp_output_dir):
        """Test generating multiple Monte Carlo samples with new interface."""
        rule_config = monte_carlo_config(temp_output_dir, mode="rule")
        merged_df = simulate(rule_config)
        synth_config = monte_carlo_config(temp_output_dir, mode="synthesizer")
        samples = []
        for i in range(3):
            synthetic_df = simulate(synth_config, df=merged_df)
            assert isinstance(synthetic_df, type(merged_df))
            assert len(synthetic_df) == len(merged_df)
            samples.append(synthetic_df)


@pytest.mark.skipif(not has_synthesizer(), reason="SDV dependencies not installed")
class TestSynthesizerTypes:
    """Test different synthesizer types."""
    
    def test_gaussian_copula(self, temp_output_dir):
        """Test Gaussian Copula synthesizer (new interface)."""
        rule_config = monte_carlo_config(temp_output_dir, mode="rule")
        merged_df = simulate(rule_config)
        synth_config = monte_carlo_config(temp_output_dir, mode="synthesizer")
        synthetic_df = simulate(synth_config, df=merged_df, synthesizer_type="gaussian_copula")
        assert isinstance(synthetic_df, type(merged_df))
        assert len(synthetic_df) == len(merged_df)
    
    @pytest.mark.slow
    def test_ctgan(self, temp_output_dir):
        """Test CTGAN synthesizer (new interface, slower, neural network)."""
        rule_config = monte_carlo_config(temp_output_dir, mode="rule")
        merged_df = simulate(rule_config)
        synth_config = monte_carlo_config(temp_output_dir, mode="synthesizer")
        synthetic_df = simulate(synth_config, df=merged_df, synthesizer_type="ctgan")
        assert isinstance(synthetic_df, type(merged_df))
        assert len(synthetic_df) == len(merged_df)
    
    def test_invalid_synthesizer(self, temp_output_dir):
        """Test that invalid synthesizer type raises error."""
        synth_config = monte_carlo_config(temp_output_dir, mode="synthesizer")
        # Update config with invalid synthesizer
        with open(synth_config, 'r') as f:
            config = json.load(f)
        config["SYNTHESIZER"]["SYNTHESIZER_TYPE"] = "invalid_type"
        with open(synth_config, 'w') as f:
            json.dump(config, f, indent=2)

        # Ensure file is closed before reading
        import time
        time.sleep(0.01)

        rule_config = monte_carlo_config(temp_output_dir, mode="rule")
        merged_df = simulate(rule_config)

        from online_retail_simulator.simulator_synthesizer_based import simulate_synthesizer_based
        with pytest.raises(ValueError, match="Unknown synthesizer type"):
            simulate_synthesizer_based(merged_df, num_rows=len(merged_df), synthesizer_type="invalid_type")

