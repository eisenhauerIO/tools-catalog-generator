"""
Synthesizer-based simulation backend.
Reads a DataFrame from the path specified in config['SYNTHESIZER']['dataframe_path'].
No error handling, hard failures only.
"""

import pandas as pd



def simulate_characteristics_synthesizer_based(config):
    try:
        from sdv.single_table import GaussianCopulaSynthesizer, CTGANSynthesizer, TVAESynthesizer
        from sdv.metadata import SingleTableMetadata
    except ImportError:
        raise ImportError("SDV is required for synthesizer-based simulation. Please install SDV to use this feature.")

    path = config["SYNTHESIZER"]["dataframe_path"]
    synthesizer_type = config["SYNTHESIZER"].get("SYNTHESIZER_TYPE", "gaussian_copula")
    num_rows = config["SYNTHESIZER"].get("DEFAULT_PRODUCTS_ROWS", 10)
    df = pd.read_pickle(path)
    if synthesizer_type == "gaussian_copula":
        SynthClass = GaussianCopulaSynthesizer
    elif synthesizer_type == "ctgan":
        SynthClass = CTGANSynthesizer
    elif synthesizer_type == "tvae":
        SynthClass = TVAESynthesizer
    else:
        raise ValueError(f"Unknown synthesizer type: {synthesizer_type}")
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(df)
    synthesizer = SynthClass(metadata=metadata)
    synthesizer.fit(df)
    synthetic_df = synthesizer.sample(num_rows=num_rows)
    return synthetic_df
