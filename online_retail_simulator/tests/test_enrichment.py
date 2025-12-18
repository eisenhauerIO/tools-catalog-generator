"""Tests for enrichment functionality."""

import os
import tempfile

import pandas as pd
import pytest

from online_retail_simulator import enrich, simulate


def test_enrich_basic():
    """Test basic enrichment functionality."""
    # Create test config
    config_content = """
IMPACT:
  FUNCTION: "quantity_boost"
  PARAMS:
    effect_size: 0.5
    enrichment_fraction: 0.5
    enrichment_start: "2024-01-02"
    seed: 42
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(config_content)
        config_path = f.name

    try:
        # Generate test data
        test_config_path = os.path.join(os.path.dirname(__file__), "config_rule.yaml")
        job_info = simulate(test_config_path)

        # Apply enrichment
        enriched_job_info = enrich(config_path, job_info)

        # Load original and enriched data
        from online_retail_simulator import load_job_results

        _, original_sales = load_job_results(job_info)
        _, enriched_sales = load_job_results(enriched_job_info)

        # Verify structure
        assert isinstance(enriched_sales, pd.DataFrame)
        assert len(enriched_sales) == len(original_sales)
        assert list(enriched_sales.columns) == list(original_sales.columns)

        # Verify enrichment effect (should have some quantity increases)
        post_enrichment = enriched_sales[enriched_sales["date"] >= "2024-01-02"]
        original_post = original_sales[original_sales["date"] >= "2024-01-02"]

        # Total quantity should increase due to enrichment
        assert post_enrichment["quantity"].sum() >= original_post["quantity"].sum()

    finally:
        os.unlink(config_path)


def test_enrich_combined_boost():
    """Test combined boost with ramp-up."""
    config_content = """
IMPACT:
  FUNCTION: "combined_boost"
  PARAMS:
    effect_size: 0.3
    ramp_days: 3
    enrichment_fraction: 0.4
    enrichment_start: "2024-01-03"
    seed: 123
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(config_content)
        config_path = f.name

    try:
        # Generate test data
        test_config_path = os.path.join(os.path.dirname(__file__), "config_rule.yaml")
        job_info = simulate(test_config_path)

        # Apply enrichment
        enriched_job_info = enrich(config_path, job_info)

        # Load results
        from online_retail_simulator import load_job_results

        _, original_sales = load_job_results(job_info)
        _, enriched_sales = load_job_results(enriched_job_info)

        # Verify basic structure
        assert isinstance(enriched_sales, pd.DataFrame)
        assert len(enriched_sales) == len(original_sales)

        # Verify enrichment effect exists
        post_enrichment = enriched_sales[enriched_sales["date"] >= "2024-01-03"]
        original_post = original_sales[original_sales["date"] >= "2024-01-03"]

        assert post_enrichment["quantity"].sum() >= original_post["quantity"].sum()

    finally:
        os.unlink(config_path)


def test_enrich_invalid_config():
    """Test error handling for invalid config."""
    config_content = """
INVALID_KEY: "test"
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(config_content)
        config_path = f.name

    try:
        # Generate test data
        test_config_path = os.path.join(os.path.dirname(__file__), "config_rule.yaml")
        job_info = simulate(test_config_path)

        # Should raise error for missing IMPACT
        with pytest.raises(ValueError, match="Config must include 'IMPACT' specification"):
            enrich(config_path, job_info)

    finally:
        os.unlink(config_path)


def test_enrich_invalid_dataframe():
    """Test error handling for invalid DataFrame."""
    config_content = """
IMPACT:
  FUNCTION: "quantity_boost"
  PARAMS:
    effect_size: 0.5
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(config_content)
        config_path = f.name

    try:
        # Test with invalid job_info
        from online_retail_simulator import JobInfo

        invalid_job_info = JobInfo("invalid-job-id", ".")
        with pytest.raises(FileNotFoundError, match="Job directory not found"):
            enrich(config_path, invalid_job_info)

    finally:
        os.unlink(config_path)


def test_enrich_reproducibility():
    """Test that enrichment is reproducible with same seed."""
    config_content = """
IMPACT:
  FUNCTION: "quantity_boost"
  PARAMS:
    effect_size: 0.2
    enrichment_fraction: 0.3
    enrichment_start: "2024-01-02"
    seed: 999
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(config_content)
        config_path = f.name

    try:
        # Generate test data
        test_config_path = os.path.join(os.path.dirname(__file__), "config_rule.yaml")
        job_info = simulate(test_config_path)

        # Apply enrichment twice with same config (same seed)
        enriched_job_info1 = enrich(config_path, job_info)
        enriched_job_info2 = enrich(config_path, job_info)

        # Load results
        from online_retail_simulator import load_job_results

        _, enriched_df1 = load_job_results(enriched_job_info1)
        _, enriched_df2 = load_job_results(enriched_job_info2)

        # Results should be identical
        pd.testing.assert_frame_equal(enriched_df1, enriched_df2)

    finally:
        os.unlink(config_path)
