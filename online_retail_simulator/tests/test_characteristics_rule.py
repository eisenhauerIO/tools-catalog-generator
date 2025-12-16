import pandas as pd

from online_retail_simulator.simulate_characteristics import simulate_characteristics


def test_characteristics_rule():
    import os

    config_path = os.path.join(os.path.dirname(__file__), "config_rule.yaml")
    df = simulate_characteristics(config_path)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "asin" in df.columns
    assert "price" in df.columns
