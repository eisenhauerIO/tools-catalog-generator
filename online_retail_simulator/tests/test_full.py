"""
Test for the full simulation workflow using config_rule.yaml.
"""

import os

import pandas as pd

from online_retail_simulator.simulate import simulate


def test_simulate_full_rule():
    config_path = os.path.join(os.path.dirname(__file__), "config_rule.yaml")
    job_info = simulate(config_path)

    from online_retail_simulator import JobInfo

    assert isinstance(job_info, JobInfo)
    assert job_info.job_id.startswith("job-")

    # Load results to verify they exist
    from online_retail_simulator import load_job_results

    products_df, sales_df = load_job_results(job_info)
    assert isinstance(products_df, pd.DataFrame)
    assert isinstance(sales_df, pd.DataFrame)
    assert not products_df.empty
    assert not sales_df.empty
