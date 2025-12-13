"""Basic tests for online retail simulator."""

import pytest
import json
import tempfile
from pathlib import Path
from online_retail_simulator import generate_product_data, generate_sales_data, simulate
from online_retail_simulator.config_processor import load_defaults, deep_merge, validate_config, process_config
from online_retail_simulator.enrichment_application import assign_enrichment, parse_effect_spec, load_effect_function, apply_enrichment_to_sales


class TestProductGeneration:
    """Test product data generation."""
    
    def test_generate_products_count(self):
        """Test that correct number of products are generated."""
        products = generate_product_data(n_products=10, seed=42)
        assert len(products) == 10
    
    def test_generate_products_structure(self):
        """Test product dictionary structure."""
        products = generate_product_data(n_products=5, seed=42)
        for product in products:
            assert "product_id" in product
            assert "name" in product
            assert "category" in product
            assert "price" in product
            assert isinstance(product["price"], (int, float))
            assert product["price"] > 0
    
    def test_generate_products_reproducible(self):
        """Test that same seed produces same products."""
        products1 = generate_product_data(n_products=10, seed=42)
        products2 = generate_product_data(n_products=10, seed=42)
        assert products1 == products2
    
    def test_generate_products_categories(self):
        """Test that products have valid categories."""
        products = generate_product_data(n_products=50, seed=42)
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
        products = generate_product_data(n_products=5, seed=42)
        sales = generate_sales_data(
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
        products = generate_product_data(n_products=5, seed=42)
        sales = generate_sales_data(
            products=products,
            date_start="2024-01-01",
            date_end="2024-01-07",
            seed=42
        )
        for sale in sales:
            assert "2024-01-01" <= sale["date"] <= "2024-01-07"
    
    def test_generate_sales_reproducible(self):
        """Test that same seed produces same sales."""
        products = generate_product_data(n_products=5, seed=42)
        sales1 = generate_sales_data(
            products=products,
            date_start="2024-01-01",
            date_end="2024-01-07",
            seed=42
        )
        sales2 = generate_sales_data(
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
        products = generate_product_data(n_products=100, seed=42)
        enriched = assign_enrichment(products, fraction=0.5, seed=42)
        
        enriched_count = sum(1 for p in enriched if p.get("enriched", False))
        assert enriched_count == 50
    
    def test_assign_enrichment_reproducible(self):
        """Test enrichment assignment is reproducible."""
        products = generate_product_data(n_products=20, seed=42)
        enriched1 = assign_enrichment(products, fraction=0.5, seed=42)
        enriched2 = assign_enrichment(products, fraction=0.5, seed=42)
        
        for p1, p2 in zip(enriched1, enriched2):
            assert p1["enriched"] == p2["enriched"]


class TestEffectParsing:
    """Test EFFECT specification parsing."""
    
    def test_parse_shorthand_string(self):
        """Test parsing shorthand string format."""
        module, function, params = parse_effect_spec("quantity_boost:0.5")
        assert module == "enrichment_impact_library"
        assert function == "quantity_boost"
        assert params == {"effect_size": 0.5}
    
    def test_parse_shorthand_no_params(self):
        """Test parsing shorthand string without params."""
        module, function, params = parse_effect_spec("quantity_boost")
        assert module == "enrichment_impact_library"
        assert function == "quantity_boost"
        assert params == {}
    
    def test_parse_dict_basic(self):
        """Test parsing dict format without module."""
        spec = {"function": "combined_boost", "params": {"effect_size": 0.5, "ramp_days": 7}}
        module, function, params = parse_effect_spec(spec)
        assert module == "enrichment_impact_library"
        assert function == "combined_boost"
        assert params == {"effect_size": 0.5, "ramp_days": 7}
    
    def test_parse_dict_with_module(self):
        """Test parsing dict format with custom module."""
        spec = {"module": "my_module", "function": "my_func", "params": {"param1": 10}}
        module, function, params = parse_effect_spec(spec)
        assert module == "my_module"
        assert function == "my_func"
        assert params == {"param1": 10}
    
    def test_parse_dict_no_params(self):
        """Test parsing dict format without params field."""
        spec = {"function": "quantity_boost"}
        module, function, params = parse_effect_spec(spec)
        assert module == "enrichment_impact_library"
        assert function == "quantity_boost"
        assert params == {}
    
    def test_parse_dict_missing_function(self):
        """Test parsing dict without function raises error."""
        spec = {"params": {"effect_size": 0.5}}
        with pytest.raises(ValueError, match="must include 'function'"):
            parse_effect_spec(spec)
    
    def test_parse_invalid_type(self):
        """Test parsing invalid type raises error."""
        with pytest.raises(ValueError, match="must be string or dict"):
            parse_effect_spec(123)


class TestEffectFunctions:
    """Test effect functions with new kwargs pattern."""
    
    def test_quantity_boost_with_kwargs(self):
        """Test quantity_boost with kwargs."""
        from online_retail_simulator.enrichment_impact_library import quantity_boost
        
        sale = {
            "date": "2024-01-10",
            "product_id": "P001",
            "quantity": 10,
            "unit_price": 50.0,
            "revenue": 500.0
        }
        
        result = quantity_boost(sale, enrichment_start="2024-01-05", effect_size=0.5)
        assert result["quantity"] == 15
        assert result["revenue"] == 750.0
    
    def test_combined_boost_with_kwargs(self):
        """Test combined_boost with multiple kwargs."""
        from online_retail_simulator.enrichment_impact_library import combined_boost
        
        sale = {
            "date": "2024-01-10",
            "product_id": "P001",
            "quantity": 10,
            "unit_price": 50.0,
            "revenue": 500.0
        }
        
        # 5 days into 7-day ramp, so 5/7 = 0.714 of effect_size
        result = combined_boost(
            sale, 
            enrichment_start="2024-01-05", 
            effect_size=0.7, 
            ramp_days=7
        )
        # Expected: 10 * (1 + 0.7 * (5/7)) = 10 * 1.5 = 15
        assert result["quantity"] == 15
    
    def test_apply_enrichment_with_params(self):
        """Test apply_enrichment_to_sales passes kwargs correctly."""
        products = generate_product_data(n_products=5, seed=42)
        enriched_products = assign_enrichment(products, fraction=0.5, seed=42)
        
        sales = generate_sales_data(
            products=products,
            date_start="2024-01-01",
            date_end="2024-01-20",
            seed=42
        )
        
        effect_function = load_effect_function("enrichment_impact_library", "quantity_boost")
        
        # Apply enrichment with 30% boost
        treated_sales = apply_enrichment_to_sales(
            sales,
            enriched_products,
            "2024-01-05",
            effect_function,
            effect_size=0.3
        )
        
        assert len(treated_sales) == len(sales)
        
        # Compare quantities between original and treated for enriched products after start date
        enriched_ids = {p['product_id'] for p in enriched_products if p.get('enriched', False)}
        
        quantity_increased = False
        for orig_sale, treated_sale in zip(sales, treated_sales):
            if (treated_sale['product_id'] in enriched_ids and 
                treated_sale['date'] >= "2024-01-05"):
                # These sales should have increased quantity
                if treated_sale['quantity'] > orig_sale['quantity']:
                    quantity_increased = True
                    break
        
        # At least one sale should have increased quantity due to treatment
        assert quantity_increased


class TestConfigProcessor:
    """Test configuration processing."""
    
    def test_load_defaults(self):
        """Test loading default configuration."""
        defaults = load_defaults()
        assert "SEED" in defaults
        assert "OUTPUT_DIR" in defaults
        assert "BASELINE" in defaults
        assert "ENRICHMENT" in defaults
        # Check new EFFECT field exists
        assert "EFFECT" in defaults["ENRICHMENT"]
        # Check old fields are removed
        assert "EFFECT_MODULE" not in defaults["ENRICHMENT"]
        assert "EFFECT_FUNCTION" not in defaults["ENRICHMENT"]
        assert "EFFECT_SIZE" not in defaults["ENRICHMENT"]
    
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
            assert config["ENRICHMENT"]["EFFECT"] == "quantity_boost:0.5"  # From defaults
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
            
            products_df, sales_df = simulate(str(config_path))
            
            # Check output files exist
            assert (Path(tmpdir) / "products.json").exists()
            assert (Path(tmpdir) / "sales.json").exists()
            
            # Verify DataFrames returned
            assert len(products_df) == 10
            assert len(sales_df) > 0
            
            # Verify JSON is valid
            with open(Path(tmpdir) / "products.json") as f:
                products = json.load(f)
                assert len(products) == 10
            
            with open(Path(tmpdir) / "sales.json") as f:
                sales = json.load(f)
                assert len(sales) > 0
    
    def test_simulate_with_enrichment_shorthand(self):
        """Test simulation with enrichment using shorthand EFFECT."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                "SEED": 42,
                "OUTPUT_DIR": tmpdir,
                "BASELINE": {
                    "NUM_PRODUCTS": 10,
                    "DATE_START": "2024-01-01",
                    "DATE_END": "2024-01-31",
                    "PRODUCTS_FILE": "products.json",
                    "SALES_FILE": "sales.json"
                },
                "ENRICHMENT": {
                    "START_DATE": "2024-01-15",
                    "FRACTION": 0.5,
                    "EFFECT": "quantity_boost:0.5",
                    "PRODUCTS_FILE": "products_enriched.json",
                    "SALES_FACTUAL_FILE": "sales_factual.json",
                    "SALES_COUNTERFACTUAL_FILE": "sales_counterfactual.json"
                }
            }
            
            config_path = Path(tmpdir) / "config.json"
            with open(config_path, 'w') as f:
                json.dump(config, f)
            
            products_df, sales_df = simulate(str(config_path))
            
            # Check all output files exist
            assert (Path(tmpdir) / "products.json").exists()
            assert (Path(tmpdir) / "sales.json").exists()
            assert (Path(tmpdir) / "products_enriched.json").exists()
            assert (Path(tmpdir) / "sales_factual.json").exists()
            assert (Path(tmpdir) / "sales_counterfactual.json").exists()
            
            # Verify DataFrames returned
            assert len(products_df) == 10
            assert len(sales_df) > 0
            
            # Verify factual revenue is higher than counterfactual
            with open(Path(tmpdir) / "sales_factual.json") as f:
                factual = json.load(f)
                factual_revenue = sum(s["revenue"] for s in factual)
            
            with open(Path(tmpdir) / "sales_counterfactual.json") as f:
                counterfactual = json.load(f)
                counterfactual_revenue = sum(s["revenue"] for s in counterfactual)
            
            assert factual_revenue > counterfactual_revenue
    
    def test_simulate_with_enrichment_dict(self):
        """Test simulation with enrichment using dict EFFECT."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                "SEED": 42,
                "OUTPUT_DIR": tmpdir,
                "BASELINE": {
                    "NUM_PRODUCTS": 10,
                    "DATE_START": "2024-01-01",
                    "DATE_END": "2024-01-31",
                    "PRODUCTS_FILE": "products.json",
                    "SALES_FILE": "sales.json"
                },
                "ENRICHMENT": {
                    "START_DATE": "2024-01-15",
                    "FRACTION": 0.5,
                    "EFFECT": {
                        "function": "combined_boost",
                        "params": {"effect_size": 0.5, "ramp_days": 7}
                    },
                    "PRODUCTS_FILE": "products_enriched.json",
                    "SALES_FACTUAL_FILE": "sales_factual.json",
                    "SALES_COUNTERFACTUAL_FILE": "sales_counterfactual.json"
                }
            }
            
            config_path = Path(tmpdir) / "config.json"
            with open(config_path, 'w') as f:
                json.dump(config, f)
            
            products_df, sales_df = simulate(str(config_path))
            
            # Check all output files exist
            assert (Path(tmpdir) / "products_enriched.json").exists()
            assert (Path(tmpdir) / "sales_factual.json").exists()
            assert (Path(tmpdir) / "sales_counterfactual.json").exists()
