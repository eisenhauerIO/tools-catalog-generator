"""Tests for product-aware enrichment functionality (product_detail_boost)."""

import os
import tempfile

import pandas as pd
import pytest

from conftest import OLLAMA_AVAILABLE
from online_retail_simulator import enrich, load_job_results, simulate
from online_retail_simulator.enrich.enrichment_library import _regenerate_product_details


def test_product_detail_boost_basic():
    """Test basic product_detail_boost functionality."""
    config_content = """
IMPACT:
  FUNCTION: "product_detail_boost"
  PARAMS:
    effect_size: 0.5
    enrichment_fraction: 0.5
    enrichment_start: "2024-01-02"
    seed: 42
    backend: "mock"
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(config_content)
        config_path = f.name

    try:
        # Generate test data
        test_config_path = os.path.join(os.path.dirname(__file__), "config_rule.yaml")
        job_info = simulate(test_config_path)

        # Load original sales before enrichment
        original_metrics = job_info.load_df("metrics")

        # Apply enrichment
        enriched_job_info = enrich(config_path, job_info)

        # Load enriched data
        enriched_metrics = enriched_job_info.load_df("enriched")

        # Verify structure
        assert isinstance(enriched_metrics, pd.DataFrame)
        assert len(enriched_metrics) == len(original_metrics)

        # Verify enrichment effect (should have some ordered units increases)
        post_enrichment = enriched_metrics[enriched_metrics["date"] >= "2024-01-02"]
        original_post = original_metrics[original_metrics["date"] >= "2024-01-02"]

        # Total ordered units should increase due to enrichment
        assert post_enrichment["ordered_units"].sum() >= original_post["ordered_units"].sum()

    finally:
        os.unlink(config_path)


def test_product_detail_boost_saves_original_products():
    """Test that product_detail_boost saves original products."""
    config_content = """
IMPACT:
  FUNCTION: "product_detail_boost"
  PARAMS:
    effect_size: 0.3
    enrichment_fraction: 0.5
    enrichment_start: "2024-01-02"
    seed: 42
    backend: "mock"
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

        # Check that product_details_original was saved
        original_details = enriched_job_info.load_df("product_details_original")
        assert original_details is not None
        assert isinstance(original_details, pd.DataFrame)
        assert len(original_details) > 0

    finally:
        os.unlink(config_path)


def test_product_detail_boost_saves_enriched_products():
    """Test that product_detail_boost saves enriched products with flag."""
    config_content = """
IMPACT:
  FUNCTION: "product_detail_boost"
  PARAMS:
    effect_size: 0.3
    enrichment_fraction: 0.5
    enrichment_start: "2024-01-02"
    seed: 42
    backend: "mock"
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

        # Check that product_details_enriched was saved
        enriched_details = enriched_job_info.load_df("product_details_enriched")
        assert enriched_details is not None
        assert isinstance(enriched_details, pd.DataFrame)
        assert len(enriched_details) > 0

        # Check that enriched flag exists
        assert "enriched" in enriched_details.columns

        # Check that some products are marked as enriched
        n_enriched = enriched_details["enriched"].sum()
        assert n_enriched > 0

        # Check that both enriched and non-enriched products exist
        n_control = len(enriched_details) - n_enriched
        assert n_control > 0

    finally:
        os.unlink(config_path)


def test_product_detail_boost_load_job_results():
    """Test that load_job_results includes product details files."""
    config_content = """
IMPACT:
  FUNCTION: "product_detail_boost"
  PARAMS:
    effect_size: 0.3
    enrichment_fraction: 0.5
    enrichment_start: "2024-01-02"
    seed: 42
    backend: "mock"
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

        # Load all results
        results = load_job_results(enriched_job_info)

        # Check that product details are included
        assert "product_details_original" in results
        assert "product_details_enriched" in results
        assert "products" in results
        assert "metrics" in results
        assert "enriched" in results

    finally:
        os.unlink(config_path)


def test_regenerate_product_details_helper():
    """Test the _regenerate_product_details helper function."""
    products = [
        {"product_identifier": "A001", "category": "Electronics", "price": 99.99, "title": "Old Title 1"},
        {"product_identifier": "A002", "category": "Electronics", "price": 49.99, "title": "Old Title 2"},
        {"product_identifier": "A003", "category": "Clothing", "price": 29.99, "title": "Old Title 3"},
    ]
    treatment_ids = {"A001", "A003"}

    updated = _regenerate_product_details(products, treatment_ids, None, "mock", 42, quality_boost=0.0)

    # Check all products are returned
    assert len(updated) == 3

    # Check enriched flag
    enriched_flags = {p["product_identifier"]: p["enriched"] for p in updated}
    assert enriched_flags["A001"] is True
    assert enriched_flags["A002"] is False
    assert enriched_flags["A003"] is True

    # Check treatment products have new titles (from mock treatment mode)
    for p in updated:
        if p["product_identifier"] in treatment_ids:
            assert "title" in p
            # Treatment mode uses different adjectives/brands


def test_product_detail_boost_reproducibility():
    """Test that product_detail_boost is reproducible with same seed."""
    config_content = """
IMPACT:
  FUNCTION: "product_detail_boost"
  PARAMS:
    effect_size: 0.2
    enrichment_fraction: 0.3
    enrichment_start: "2024-01-02"
    seed: 999
    backend: "mock"
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(config_content)
        config_path = f.name

    try:
        # Generate same test data twice (with fixed seed in config)
        test_config_path = os.path.join(os.path.dirname(__file__), "config_rule.yaml")
        job_info1 = simulate(test_config_path)
        job_info2 = simulate(test_config_path)

        # Apply enrichment with same config
        enriched_job1 = enrich(config_path, job_info1)
        enriched_job2 = enrich(config_path, job_info2)

        # Load enriched products
        enriched1 = enriched_job1.load_df("product_details_enriched")
        enriched2 = enriched_job2.load_df("product_details_enriched")

        # Same number of enriched products
        assert enriched1["enriched"].sum() == enriched2["enriched"].sum()

    finally:
        os.unlink(config_path)


@pytest.mark.llm
@pytest.mark.skipif(not OLLAMA_AVAILABLE, reason="Ollama server not available")
def test_product_detail_boost_with_ollama():
    """Test product_detail_boost with actual Ollama backend."""
    config_content = """
IMPACT:
  FUNCTION: "product_detail_boost"
  PARAMS:
    effect_size: 0.3
    enrichment_fraction: 0.3
    enrichment_start: "2024-01-02"
    seed: 42
    backend: "ollama"
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(config_content)
        config_path = f.name

    try:
        # Generate test data
        test_config_path = os.path.join(os.path.dirname(__file__), "config_rule.yaml")
        job_info = simulate(test_config_path)

        # Apply enrichment with Ollama backend
        enriched_job_info = enrich(config_path, job_info)

        # Load enriched products
        enriched_details = enriched_job_info.load_df("product_details_enriched")
        assert enriched_details is not None
        assert isinstance(enriched_details, pd.DataFrame)

        # Check that enriched flag exists and some products are enriched
        assert "enriched" in enriched_details.columns
        n_enriched = enriched_details["enriched"].sum()
        assert n_enriched > 0

        # Check that enriched products have titles and descriptions
        enriched_products = enriched_details[enriched_details["enriched"]]
        assert all(enriched_products["title"].notna())
        assert all(enriched_products["description"].notna())

    finally:
        os.unlink(config_path)
