"""
Example script demonstrating the online-retail-simulator package.

This script shows two use cases:
1. Basic retail data generation (rule-based)
2. Synthesizer-based generation (SDV) - if available
"""

from online_retail_simulator import simulate


def main():
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Rule-Based Generation")
    print("=" * 70)
    print("Generating synthetic product catalog and sales transactions (rule-based).\n")

    # Run rule-based simulation
    rule_df = simulate("demo/config_rule.yaml")
    print(f"✓ Generated {len(rule_df)} sales records using rule-based simulation")
    print("✓ Files saved to demo/output/")

    print("\n" + "=" * 70)
    print("EXAMPLE 2: Synthesizer-Based Generation")
    print("=" * 70)
    print("Attempting synthesizer-based generation (requires SDV)...\n")

    try:
        # Try synthesizer-based simulation
        synth_df = simulate("demo/config_synthesizer.yaml")
        print(f"✓ Generated {len(synth_df)} sales records using synthesizer-based simulation")
        print("✓ Files saved to demo/output_mc/")
    except ImportError as e:
        print(f"✗ Synthesizer simulation not available: {e}")
        print("  Install with: pip install online-retail-simulator[synthesizer]")

    print("\n" + "=" * 70)
    print("Examples complete")
    print("=" * 70)
    print("Check demo/output/ for rule-based results.")
    print("Check demo/output_mc/ for synthesizer results (if SDV is available).\n")


if __name__ == "__main__":
    main()
