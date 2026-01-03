"""Tests for product details simulation."""

import pandas as pd
import pytest

from online_retail_simulator.simulate.product_details_mock import simulate_product_details_mock


@pytest.fixture
def sample_products():
    """Sample products DataFrame for testing."""
    return pd.DataFrame(
        [
            {"asin": "A001", "category": "Electronics", "price": 99.99},
            {"asin": "A002", "category": "Clothing", "price": 29.99},
            {"asin": "A003", "category": "Home & Kitchen", "price": 49.99},
        ]
    )


class TestProductDetailsMock:
    """Tests for mock backend."""

    def test_adds_required_columns(self, sample_products):
        """Mock should add title, description, brand, features."""
        result = simulate_product_details_mock(sample_products)
        assert "title" in result.columns
        assert "description" in result.columns
        assert "brand" in result.columns
        assert "features" in result.columns

    def test_preserves_original_columns(self, sample_products):
        """Mock should preserve original columns."""
        result = simulate_product_details_mock(sample_products)
        assert "asin" in result.columns
        assert "category" in result.columns
        assert "price" in result.columns

    def test_preserves_row_count(self, sample_products):
        """Mock should return same number of rows."""
        result = simulate_product_details_mock(sample_products)
        assert len(result) == len(sample_products)

    def test_seed_reproducibility(self, sample_products):
        """Same seed should produce same results."""
        result1 = simulate_product_details_mock(sample_products, seed=42)
        result2 = simulate_product_details_mock(sample_products, seed=42)
        pd.testing.assert_frame_equal(result1, result2)

    def test_different_seeds_differ(self, sample_products):
        """Different seeds should produce different results."""
        result1 = simulate_product_details_mock(sample_products, seed=42)
        result2 = simulate_product_details_mock(sample_products, seed=123)
        assert not result1["title"].equals(result2["title"])

    def test_features_is_list(self, sample_products):
        """Features should be a list."""
        result = simulate_product_details_mock(sample_products)
        assert isinstance(result["features"].iloc[0], list)


class TestProductDetailsOllama:
    """Tests for Ollama backend (skipped if not running)."""

    @pytest.fixture
    def ollama_available(self):
        """Check if Ollama is running."""
        import requests

        try:
            resp = requests.get("http://localhost:11434/api/tags", timeout=2)
            return resp.status_code == 200
        except Exception:
            return False

    def test_ollama_generates_details(self, sample_products, ollama_available):
        """Ollama should generate product details."""
        if not ollama_available:
            pytest.skip("Ollama not running")

        from online_retail_simulator.simulate.product_details_ollama import simulate_product_details_ollama

        result = simulate_product_details_ollama(sample_products)

        assert "title" in result.columns
        assert "description" in result.columns
        assert "brand" in result.columns
        assert "features" in result.columns
        assert len(result) == len(sample_products)
