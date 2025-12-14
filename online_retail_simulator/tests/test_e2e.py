
import pytest
from .import_helpers import has_synthesizer
from pathlib import Path
from online_retail_simulator.simulator import simulate
from online_retail_simulator.enrichment_application import enrich


def test_e2e_rule_based():
    rule_config = str(Path(__file__).parent / "config_rule.json")
    merged_df = simulate(rule_config)
    assert merged_df is not None
    assert not merged_df.empty

@pytest.mark.skipif(not has_synthesizer(), reason="SDV dependencies not installed")
def test_e2e_synthesizer_based():
    rule_config = str(Path(__file__).parent / "config_rule.json")
    synth_config = str(Path(__file__).parent / "config_synthesizer.json")
    merged_df = simulate(rule_config)
    assert merged_df is not None
    assert not merged_df.empty
    synthetic_df = simulate(synth_config, df=merged_df)
    assert synthetic_df is not None
    assert not synthetic_df.empty
    assert synthetic_df.shape == merged_df.shape
    # Enrichment step
    enriched_df = enrich(synth_config, synthetic_df)
    assert enriched_df is not None
    assert not enriched_df.empty
    assert enriched_df.shape[0] == synthetic_df.shape[0]

