"""Basic tests for online retail simulator."""

import pytest
import json
import tempfile
from pathlib import Path
from online_retail_simulator import generate_products, generate_sales, simulate
from online_retail_simulator.config_processor import load_defaults, deep_merge, validate_config, process_config
from online_retail_simulator.enrichment_application import assign_enrichment


class TestProductGeneration:
    """Test product data generation."""
    
    def test_generate_products_count(self):
        """Test that correct number of products are generated."""
        products = generate_products(n_products=10, seed=42)
        assert len(products) == 10
    
    def test_generate_products_structure(self):
        """Test product dictionary structure."""
        products = generate_products(n_products=5, seed=42)
        for product in products:
            assert "product_id" in product
            assert "name" in product
            assert "category" in product
            assert "price" in product
            assert isinstance(product["price"], (int, float))
            assert product["price"] > 0
    
    def test_generate_products_reproducible(self):
        """Test that same seed produces same products."""
        products1 = generate_products(n_products=10, seed=42)
        products2 = generate_products(n_products=10, seed=42)
        assert products1 == products2
    
    def test_generate_products_categories(self):
        """Test that products have valid categories."""
        products = generate_products(n_products=50, seed=42)
        categories = {p["category"] for p in products}
        valid_categories = {
            "Electronics", "Clothing", "Home & Garden", "Books",
            "Sports & Outdoors", "Toys & Games", "Food & Beverage", "Health & Beauty"
        }
        assert categories.issubset(valid_categories)


class TestSalesGeneration:
    """Test sales data generation."""
    
    def test_generate_sales_basic(self):
        """Test basic sales generation."""
        products = generate_products(n_products=5, seed=42)
        sales = generate_sales(
            products=products,
            date_start="2024-01-01",
            date_end="2024-01-07",
            seed=42
        )
        assert len(sales) > 0
        assert all("date" in sale for sale in sales)
        assert all("product_id" in sale for sale in sales)
        assert all("quantity" in sale for sale in sales)
        assert all("revenue" in sale for sale in sales)
    
    def test_generate_sales_date_range(self):
        """Test sales are within specified date range."""
        products = generate_products(n_products=5, seed=42)
        sales = generate_sales(
            products=products,
            date_start="2024-01-01",
            date_end="2024-01-07",
            seed=42
        )
        for sale in sales:
            assert "2024-01-01" <= sale["date"] <= "2024-01-07"
    
    def test_generate_sales_reproducible(self):
        """Test that same seed produces same sales."""
        products = generate_products(n_products=5, seed=42)
        sales1 = generate_sales(
            products=products,
            date_start="2024-01-01",
            date_end="2024-01-07",
            seed=42
        )
        sales2 = generate_sales(
            products=products,
            date_start="2024-01-01",
            date_end="2024-01-07",
            seed=42
        )
        assert sales1 == sales2


class TestEnrichmentAssignment:
    """Test enrichment assignment."""
    
    def test_assign_enrichment_fraction(self):
        """Test correct fraction of products are enriched."""
        products = generate_products(n_products=100, seed=42)
        enriched = assign_enrichment(products, fraction=0.5, seed=42)
        
        enriched_count = sum(1 for p in enriched if p.get("enriched", False))
        assert enriched_count == 50
    
    def test_assign_enrichment_reproducible(self):
        """Test enrichment assignment is reproducible."""
        products = generate_products(n_products=20, seed=42)
        enriched1 = assign_enrichment(products, fraction=0.5, seed=42)
        enriched2 = assign_enrichment(products, fraction=0.5, seed=42)
        
        for p1, p2 in zip(enriched1, enriched2):
            assert p1["enriched"] == p2["enriched"]


class TestConfigProcessor:
    """Test configuration processing."""
    
    def test_load_defaults(self):
        """Test loading default configuration."""
        defaults = load_defaults()
        assert "SEED" in defaults
        assert "OUTPUT_DIR" in defaults
        assert "BASELINE" in defaults
        assert "ENRICHMENT" in defaults
    
    def test_deep_merge(self):
        """Test deep merge of configurations."""
        base = {"a": 1, "b": {"c": 2, "d": 3}}
        override = {"b": {"c": 4}, "e": 5}
        result = deep_merge(base, override)
        
        assert result["a"] == 1
        assert result["b"]["c"] == 4
        assert result["b"]["d"] == 3
        assert result["e"] == 5
    
    def test_validate_config_missing_baseline(self):
        """Test validation fails without BASELINE."""
        config = {"SEED": 42}
        with pytest.raises(ValueError, match="must include BASELINE"):
            validate_config(config)
    
    def test_validate_config_missing_dates(self):
        """Test validation fails without required dates."""
        config = {"BASELINE": {}}
        with pytest.raises(ValueError, match="DATE_START is required"):
            validate_config(config)
    
    def test_process_config_with_defaults(self):
        """Test config processing applies defaults."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "BASELINE": {
                    "DATE_START": "2024-01-01",
                    "DATE_END": "2024-01-31"
                }
            }, f)
            config_path = f.name
        
        try:
            config = process_config(config_path)
            assert config["SEED"] == 42  # From defaults
            assert config["BASELINE"]["NUM_PRODUCTS"] == 100  # From defaults
            assert config["BASELINE"]["DATE_START"] == "2024-01-01"  # From user
        finally:
            Path(config_path).unlink()


class TestEndToEnd:
    """End-to-end integration tests."""
    
    def test_simulate_basic(self):
        """Test basic simulation runs without error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                "SEED": 42,
                "OUTPUT_DIR": tmpdir,
                "BASELINE": {
                    "NUM_PRODUCTS": 10,
                    "DATE_START": "2024-01-01",
                    "DATE_END": "2024-01-07",
                    "PRODUCTS_FILE": "products.json",
                    "SALES_FILE": "sales.json"
                }
            }
            
            config_path = Path(tmpdir) / "config.json"
            with open(config_path, 'w') as f:
                json.dump(config, f)
            
            simulate(str(config_path))
            
            # Check output files exist
            assert (Path(tmpdir) / "products.json").exists()
            assert (Path(tmpdir) / "sales.json").exists()
            
            # Verify JSON is valid
            with open(Path(tmpdir) / "products.json") as f:
                products = json.load(f)
                assert len(products) == 10
            
            with open(Path(tmpdir) / "sales.json") as f:
                sales = json.load(f)
                assert len(sales) > 0
