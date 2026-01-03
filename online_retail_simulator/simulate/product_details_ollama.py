"""Product details generation using Ollama (local LLM)."""

import json

import pandas as pd
import requests

OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "mistral:latest"
DEFAULT_BATCH_SIZE = 5

PROMPT_TEMPLATE = """Generate product details for these e-commerce products.

Products:
{products_json}

For each product, generate:
- title: Product title (50-100 chars)
- description: Product description (100-300 chars)
- brand: Realistic brand name
- features: List of 3-5 features

Return a JSON array with all original fields plus the new fields.
Keep the same order as input.
Only return valid JSON, no other text."""


def simulate_product_details_ollama(
    products_df: pd.DataFrame,
    model: str = DEFAULT_MODEL,
    ollama_url: str = OLLAMA_URL,
) -> pd.DataFrame:
    """Generate product details using Ollama (local LLM).

    Args:
        products_df: Input products with asin, category, price
        model: Ollama model to use (default: mistral:latest)
        ollama_url: Ollama API URL (default: http://localhost:11434)

    Returns:
        DataFrame with added title, description, brand, features
    """
    results = []
    products = products_df.to_dict("records")

    for i in range(0, len(products), DEFAULT_BATCH_SIZE):
        batch = products[i : i + DEFAULT_BATCH_SIZE]
        prompt = PROMPT_TEMPLATE.format(products_json=json.dumps(batch, indent=2))

        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120,
        )
        response.raise_for_status()

        response_text = response.json().get("response", "")
        batch_results = json.loads(response_text)
        results.extend(batch_results)

    return pd.DataFrame(results)
