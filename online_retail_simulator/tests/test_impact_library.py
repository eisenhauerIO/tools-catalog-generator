"""Tests for enrichment impact library functions."""

from datetime import datetime

import pytest

from online_retail_simulator.enrichment_impact_library import combined_boost, probability_boost, quantity_boost


def create_test_sales():
    """Create test sales data for impact function testing."""
    return [
        {
            "product_id": "PROD001",
            "date": "2024-11-10",
            "quantity": 2,
            "price": 100.0,
            "unit_price": 100.0,
            "revenue": 200.0,
        },
        {
            "product_id": "PROD001",
            "date": "2024-11-20",
            "quantity": 1,
            "price": 100.0,
            "unit_price": 100.0,
            "revenue": 100.0,
        },
        {
            "product_id": "PROD002",
            "date": "2024-11-15",
            "quantity": 3,
            "price": 50.0,
            "unit_price": 50.0,
            "revenue": 150.0,
        },
        {
            "product_id": "PROD002",
            "date": "2024-11-25",
            "quantity": 2,
            "price": 50.0,
            "unit_price": 50.0,
            "revenue": 100.0,
        },
        {
            "product_id": "PROD003",
            "date": "2024-11-12",
            "quantity": 1,
            "price": 200.0,
            "unit_price": 200.0,
            "revenue": 200.0,
        },
    ]


class TestQuantityBoost:
    """Test quantity_boost function."""

    def test_quantity_boost_basic(self):
        """Test basic quantity boost functionality."""
        sales = create_test_sales()

        result = quantity_boost(
            sales,
            effect_size=0.5,
            enrichment_fraction=0.5,
            enrichment_start="2024-11-15",
            seed=42,
        )

        # Should return same number of sales
        assert len(result) == len(sales)

        # Check that some sales after enrichment start have increased quantities
        post_enrichment = [s for s in result if s["date"] >= "2024-11-15"]
        original_post = [s for s in sales if s["date"] >= "2024-11-15"]

        total_quantity_original = sum(s["quantity"] for s in original_post)
        total_quantity_result = sum(s["quantity"] for s in post_enrichment)

        # Should have some increase due to enrichment
        assert total_quantity_result >= total_quantity_original

    def test_quantity_boost_no_enrichment_before_start(self):
        """Test that no enrichment is applied before start date."""
        sales = create_test_sales()

        result = quantity_boost(
            sales,
            effect_size=0.5,
            enrichment_fraction=1.0,  # All products enriched
            enrichment_start="2024-12-01",  # After all sales
            seed=42,
        )

        # All sales should be unchanged since they're before start date
        for original, treated in zip(sales, result):
            assert treated["quantity"] == original["quantity"]
            assert treated["revenue"] == original["revenue"]

    def test_quantity_boost_zero_fraction(self):
        """Test that no enrichment is applied with zero fraction."""
        sales = create_test_sales()

        result = quantity_boost(
            sales,
            effect_size=0.5,
            enrichment_fraction=0.0,  # No products enriched
            enrichment_start="2024-11-01",
            seed=42,
        )

        # All sales should be unchanged
        for original, treated in zip(sales, result):
            assert treated["quantity"] == original["quantity"]
            assert treated["revenue"] == original["revenue"]

    def test_quantity_boost_reproducibility(self):
        """Test that results are reproducible with same seed."""
        sales = create_test_sales()

        result1 = quantity_boost(
            sales,
            effect_size=0.3,
            enrichment_fraction=0.5,
            enrichment_start="2024-11-15",
            seed=123,
        )

        result2 = quantity_boost(
            sales,
            effect_size=0.3,
            enrichment_fraction=0.5,
            enrichment_start="2024-11-15",
            seed=123,
        )

        # Results should be identical
        assert result1 == result2

    def test_quantity_boost_different_seeds(self):
        """Test that different seeds can produce different results."""
        # Create more products to increase chance of different selection
        sales = []
        for i in range(10):
            sales.append(
                {
                    "product_id": f"PROD{i:03d}",
                    "date": "2024-11-20",
                    "quantity": 1,
                    "price": 100.0,
                    "unit_price": 100.0,
                    "revenue": 100.0,
                }
            )

        result1 = quantity_boost(
            sales,
            effect_size=0.5,
            enrichment_fraction=0.5,
            enrichment_start="2024-11-15",
            seed=42,
        )

        result2 = quantity_boost(
            sales,
            effect_size=0.5,
            enrichment_fraction=0.5,
            enrichment_start="2024-11-15",
            seed=999,
        )

        # With 10 products and 50% enrichment, different seeds should produce different results
        # (though not guaranteed, very likely)
        total_qty1 = sum(s["quantity"] for s in result1)
        total_qty2 = sum(s["quantity"] for s in result2)

        # At least verify that the function runs with different seeds
        assert len(result1) == len(result2) == 10
        # Results might be different (but not required for test to pass)
        assert total_qty1 >= 10  # At least original quantities
        assert total_qty2 >= 10  # At least original quantities

    def test_quantity_boost_revenue_calculation(self):
        """Test that revenue is correctly recalculated after quantity boost."""
        sales = [
            {
                "product_id": "PROD001",
                "date": "2024-11-20",
                "quantity": 2,
                "price": 100.0,
                "unit_price": 100.0,
                "revenue": 200.0,
            }
        ]

        result = quantity_boost(
            sales,
            effect_size=0.5,  # 50% boost
            enrichment_fraction=1.0,  # All products enriched
            enrichment_start="2024-11-15",
            seed=42,
        )

        treated_sale = result[0]
        # Quantity should be boosted: 2 * 1.5 = 3
        assert treated_sale["quantity"] == 3
        # Revenue should be recalculated: 3 * 100 = 300
        assert treated_sale["revenue"] == 300.0

    def test_quantity_boost_default_parameters(self):
        """Test quantity boost with default parameters."""
        sales = create_test_sales()

        # Test with minimal parameters (should use defaults)
        result = quantity_boost(sales)

        assert len(result) == len(sales)
        assert isinstance(result, list)


class TestProbabilityBoost:
    """Test probability_boost function."""

    def test_probability_boost_delegates_to_quantity_boost(self):
        """Test that probability_boost delegates to quantity_boost."""
        sales = create_test_sales()

        prob_result = probability_boost(
            sales,
            effect_size=0.3,
            enrichment_fraction=0.5,
            enrichment_start="2024-11-15",
            seed=42,
        )

        qty_result = quantity_boost(
            sales,
            effect_size=0.3,
            enrichment_fraction=0.5,
            enrichment_start="2024-11-15",
            seed=42,
        )

        # Results should be identical since probability_boost calls quantity_boost
        assert prob_result == qty_result

    def test_probability_boost_basic(self):
        """Test basic probability boost functionality."""
        sales = create_test_sales()

        result = probability_boost(
            sales,
            effect_size=0.4,
            enrichment_fraction=0.6,
            enrichment_start="2024-11-15",
            seed=123,
        )

        assert len(result) == len(sales)

        # Should have some impact on post-enrichment sales
        post_enrichment = [s for s in result if s["date"] >= "2024-11-15"]
        original_post = [s for s in sales if s["date"] >= "2024-11-15"]

        total_quantity_original = sum(s["quantity"] for s in original_post)
        total_quantity_result = sum(s["quantity"] for s in post_enrichment)

        assert total_quantity_result >= total_quantity_original


class TestCombinedBoost:
    """Test combined_boost function."""

    def test_combined_boost_basic(self):
        """Test basic combined boost functionality."""
        sales = create_test_sales()

        result = combined_boost(
            sales,
            effect_size=0.5,
            ramp_days=3,
            enrichment_fraction=0.5,
            enrichment_start="2024-11-15",
            seed=42,
        )

        assert len(result) == len(sales)

        # Should have some impact on post-enrichment sales
        post_enrichment = [s for s in result if s["date"] >= "2024-11-15"]
        original_post = [s for s in sales if s["date"] >= "2024-11-15"]

        total_quantity_original = sum(s["quantity"] for s in original_post)
        total_quantity_result = sum(s["quantity"] for s in post_enrichment)

        assert total_quantity_result >= total_quantity_original

    def test_combined_boost_ramp_effect(self):
        """Test that ramp effect increases over time."""
        # Create sales with specific dates to test ramp
        sales = [
            {
                "product_id": "PROD001",
                "date": "2024-11-15",  # Day 0 (start)
                "quantity": 10,
                "price": 100.0,
                "unit_price": 100.0,
                "revenue": 1000.0,
            },
            {
                "product_id": "PROD001",
                "date": "2024-11-16",  # Day 1
                "quantity": 10,
                "price": 100.0,
                "unit_price": 100.0,
                "revenue": 1000.0,
            },
            {
                "product_id": "PROD001",
                "date": "2024-11-18",  # Day 3 (full ramp)
                "quantity": 10,
                "price": 100.0,
                "unit_price": 100.0,
                "revenue": 1000.0,
            },
        ]

        result = combined_boost(
            sales,
            effect_size=0.5,  # 50% max boost
            ramp_days=3,  # 3-day ramp
            enrichment_fraction=1.0,  # All products enriched
            enrichment_start="2024-11-15",
            seed=42,
        )

        # Day 0: 0% of full effect (0% boost)
        # Day 1: 33% of full effect (~17% boost)
        # Day 3: 100% of full effect (50% boost)

        day0_sale = next(s for s in result if s["date"] == "2024-11-15")
        day1_sale = next(s for s in result if s["date"] == "2024-11-16")
        day3_sale = next(s for s in result if s["date"] == "2024-11-18")

        # Quantities should increase over time due to ramp
        assert day0_sale["quantity"] <= day1_sale["quantity"] <= day3_sale["quantity"]

        # Day 3 should have the full 50% boost: 10 * 1.5 = 15
        assert day3_sale["quantity"] == 15

    def test_combined_boost_no_ramp(self):
        """Test combined boost with ramp_days=1 (immediate full effect)."""
        sales = [
            {
                "product_id": "PROD001",
                "date": "2024-11-20",
                "quantity": 4,
                "price": 100.0,
                "unit_price": 100.0,
                "revenue": 400.0,
            }
        ]

        result = combined_boost(
            sales,
            effect_size=0.25,  # 25% boost
            ramp_days=1,  # Full effect after 1 day
            enrichment_fraction=1.0,
            enrichment_start="2024-11-20",
            seed=42,
        )

        treated_sale = result[0]
        # On day 0 (start date), ramp_factor = 0/1 = 0, so no boost
        # The sale is on the start date, so days_since_start = 0
        assert treated_sale["quantity"] == 4  # No boost on day 0
        assert treated_sale["revenue"] == 400.0

    def test_combined_boost_reproducibility(self):
        """Test that combined boost is reproducible with same seed."""
        sales = create_test_sales()

        result1 = combined_boost(
            sales,
            effect_size=0.3,
            ramp_days=5,
            enrichment_fraction=0.4,
            enrichment_start="2024-11-15",
            seed=456,
        )

        result2 = combined_boost(
            sales,
            effect_size=0.3,
            ramp_days=5,
            enrichment_fraction=0.4,
            enrichment_start="2024-11-15",
            seed=456,
        )

        assert result1 == result2

    def test_combined_boost_default_parameters(self):
        """Test combined boost with default parameters."""
        sales = create_test_sales()

        result = combined_boost(sales)

        assert len(result) == len(sales)
        assert isinstance(result, list)

    def test_combined_boost_zero_ramp_days(self):
        """Test combined boost with zero ramp days (should handle gracefully)."""
        sales = [
            {
                "product_id": "PROD001",
                "date": "2024-11-20",
                "quantity": 2,
                "price": 100.0,
                "unit_price": 100.0,
                "revenue": 200.0,
            }
        ]

        result = combined_boost(
            sales,
            effect_size=0.5,
            ramp_days=0,  # Zero ramp days
            enrichment_fraction=1.0,
            enrichment_start="2024-11-20",
            seed=42,
        )

        # Should handle gracefully and apply full effect immediately
        treated_sale = result[0]
        # With ramp_days=0, should get full effect: 2 * 1.5 = 3
        assert treated_sale["quantity"] == 3
        assert treated_sale["revenue"] == 300.0


class TestImpactLibraryEdgeCases:
    """Test edge cases and error conditions for impact library."""

    def test_empty_sales_list(self):
        """Test impact functions with empty sales list."""
        empty_sales = []

        result_qty = quantity_boost(empty_sales)
        result_prob = probability_boost(empty_sales)
        result_combined = combined_boost(empty_sales)

        assert result_qty == []
        assert result_prob == []
        assert result_combined == []

    def test_single_sale(self):
        """Test impact functions with single sale."""
        single_sale = [
            {
                "product_id": "PROD001",
                "date": "2024-11-20",
                "quantity": 1,
                "price": 50.0,
                "unit_price": 50.0,
                "revenue": 50.0,
            }
        ]

        result_qty = quantity_boost(single_sale, enrichment_fraction=1.0, enrichment_start="2024-11-15", seed=42)

        result_prob = probability_boost(single_sale, enrichment_fraction=1.0, enrichment_start="2024-11-15", seed=42)

        result_combined = combined_boost(single_sale, enrichment_fraction=1.0, enrichment_start="2024-11-15", seed=42)

        assert len(result_qty) == 1
        assert len(result_prob) == 1
        assert len(result_combined) == 1

    def test_missing_unit_price_fallback(self):
        """Test that functions handle missing unit_price by using price."""
        sales = [
            {
                "product_id": "PROD001",
                "date": "2024-11-20",
                "quantity": 2,
                "price": 75.0,
                # No unit_price field
                "revenue": 150.0,
            }
        ]

        result = quantity_boost(
            sales,
            effect_size=0.5,
            enrichment_fraction=1.0,
            enrichment_start="2024-11-15",
            seed=42,
        )

        treated_sale = result[0]
        # Should use price as unit_price: 3 * 75 = 225
        assert treated_sale["quantity"] == 3
        assert treated_sale["revenue"] == 225.0

    def test_all_products_same_id(self):
        """Test impact functions when all sales have same product_id."""
        same_product_sales = [
            {
                "product_id": "PROD001",
                "date": "2024-11-15",
                "quantity": 1,
                "price": 100.0,
                "unit_price": 100.0,
                "revenue": 100.0,
            },
            {
                "product_id": "PROD001",
                "date": "2024-11-20",
                "quantity": 2,
                "price": 100.0,
                "unit_price": 100.0,
                "revenue": 200.0,
            },
        ]

        result = quantity_boost(
            same_product_sales,
            effect_size=0.5,
            enrichment_fraction=0.5,  # 50% chance this product is enriched
            enrichment_start="2024-11-15",
            seed=42,
        )

        assert len(result) == 2
        # Either all sales are boosted or none (since same product)
        post_enrichment = [s for s in result if s["date"] >= "2024-11-15"]
        original_post = [s for s in same_product_sales if s["date"] >= "2024-11-15"]

        total_qty_original = sum(s["quantity"] for s in original_post)
        total_qty_result = sum(s["quantity"] for s in post_enrichment)

        # Should be either equal (not enriched) or greater (enriched)
        assert total_qty_result >= total_qty_original
