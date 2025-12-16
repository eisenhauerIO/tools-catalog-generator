"""
Test for the full simulation workflow using config_rule.yaml.
"""

import os

import pandas as pd

from online_retail_simulator.simulate import simulate


def test_simulate_full_rule():
    config_path = os.path.join(os.path.dirname(__file__), "config_rule.yaml")
    df = simulate(config_path)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    # Optionally, check for expected columns or values
    # assert "some_column" in df.columns
