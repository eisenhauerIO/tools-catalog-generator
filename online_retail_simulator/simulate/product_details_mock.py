"""Mock product details generation (rule-based)."""

import random

import pandas as pd

# TODO: We need to merge this with the simulation of characteristics, so we have lists in scync.

# Mock data templates by category
MOCK_DATA = {
    "Electronics": {
        "brands": ["TechPro", "DigiMax", "SmartLife", "ElectraVolt", "NexGen"],
        "adjectives": ["Advanced", "Ultra", "Pro", "Smart", "Wireless"],
        "features": ["Long battery life", "Fast charging", "Bluetooth connectivity", "LCD display", "Voice control"],
    },
    "Home & Kitchen": {
        "brands": ["HomeStyle", "KitchenPro", "CozyLiving", "DomesticPlus", "ChefMate"],
        "adjectives": ["Premium", "Deluxe", "Essential", "Modern", "Classic"],
        "features": ["Dishwasher safe", "Heat resistant", "Non-stick coating", "Easy to clean", "Space saving"],
    },
    "Clothing": {
        "brands": ["UrbanWear", "StyleFit", "ComfortPlus", "TrendyThreads", "ClassicWear"],
        "adjectives": ["Comfortable", "Stylish", "Premium", "Casual", "Lightweight"],
        "features": ["Machine washable", "Breathable fabric", "Wrinkle resistant", "Stretch fit", "Quick dry"],
    },
    "default": {
        "brands": ["ValueBrand", "QualityFirst", "TrustMark", "PrimePick", "BestChoice"],
        "adjectives": ["Quality", "Premium", "Essential", "Classic", "Professional"],
        "features": ["High quality materials", "Durable construction", "Easy to use", "Great value", "Long lasting"],
    },
}


def _get_mock_data(category: str) -> dict:
    """Get mock data templates for a category."""
    for key in MOCK_DATA:
        if key.lower() in category.lower():
            return MOCK_DATA[key]
    return MOCK_DATA["default"]


def simulate_product_details_mock(products_df: pd.DataFrame, seed: int = None) -> pd.DataFrame:
    """Generate mock product details (rule-based).

    Args:
        products_df: Input products with asin, category, price
        seed: Random seed for reproducibility

    Returns:
        DataFrame with added title, description, brand, features
    """
    rng = random.Random(seed)
    results = []

    for product in products_df.to_dict("records"):
        category = product.get("category", "General")
        data = _get_mock_data(category)

        brand = rng.choice(data["brands"])
        adj = rng.choice(data["adjectives"])
        features = rng.sample(data["features"], min(4, len(data["features"])))

        title = f"{brand} {adj} {category} Item"
        description = f"Quality {category.lower()} product for everyday use. {features[0]}. {features[1]}."

        results.append(
            {
                **product,
                "title": title,
                "description": description,
                "brand": brand,
                "features": features,
            }
        )

    return pd.DataFrame(results)
