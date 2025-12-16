import pandas as pd
import pytest

from online_retail_simulator.simulate_characteristics import simulate_characteristics
from online_retail_simulator.simulate_metrics import simulate_metrics

from .import_helpers import has_synthesizer

pytestmark = pytest.mark.skipif(not has_synthesizer(), reason="SDV dependencies not installed")


def test_metrics_synthesizer():
    import os

    config_path = os.path.join(os.path.dirname(__file__), "config_synthesizer.yaml")
    products = simulate_characteristics(config_path)
    df = simulate_metrics(products, config_path)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "asin" in df.columns
    assert "date" in df.columns
    assert "quantity" in df.columns
    assert "revenue" in df.columns
