import pandas as pd
import pytest

from online_retail_simulator.simulate_characteristics import simulate_characteristics

from .import_helpers import has_synthesizer

pytestmark = pytest.mark.skipif(not has_synthesizer(), reason="SDV dependencies not installed")


def test_characteristics_synthesizer():
    import os

    config_path = os.path.join(os.path.dirname(__file__), "config_synthesizer.yaml")
    df = simulate_characteristics(config_path)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "product_id" in df.columns
    assert "price" in df.columns
