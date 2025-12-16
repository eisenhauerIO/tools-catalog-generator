import pandas as pd

from online_retail_simulator.simulate_characteristics import simulate_characteristics
from online_retail_simulator.simulate_metrics import simulate_metrics


def test_metrics_rule():
    import os

    config_path = os.path.join(os.path.dirname(__file__), "config_rule.yaml")
    products = simulate_characteristics(config_path)
    df = simulate_metrics(products, config_path)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "product_id" in df.columns
    assert "date" in df.columns
    assert "quantity" in df.columns
    assert "revenue" in df.columns
