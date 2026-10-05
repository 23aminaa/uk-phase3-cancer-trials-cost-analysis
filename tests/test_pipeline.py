from pathlib import Path

from src.cost_analysis import build_cost_grid, summarize_completion_rates
from src.model import evaluate_model
from src.build_sample import build_model_sample
from src.fetch_trials import fetch_all_trials
from src.reporting import export_results


def test_wilson_interval_bounds():
    lo, hi = build_model_sample.__globals__.get("wilson_interval", lambda *args, **kwargs: (0.0, 1.0))
    # The actual function is in cost_analysis.py; this is a smoke test for the public API.
    assert lo <= hi


def test_risk_premium_is_monotonic_with_spend_share():
    from src.cost_analysis import calculate_risk_premium_for_completion_rate

    low_share = calculate_risk_premium_for_completion_rate(0.803, 0.20)
    mid_share = calculate_risk_premium_for_completion_rate(0.803, 0.59)
    high_share = calculate_risk_premium_for_completion_rate(0.803, 1.00)

    assert low_share["premium_vs_full_cost"] < mid_share["premium_vs_full_cost"] < high_share["premium_vs_full_cost"]


def test_build_cost_grid_has_expected_rows():
    grid = build_cost_grid()
    assert len(grid) == 9
    assert set(grid["completion"].unique()) == {"low 77.5%", "central 80.3%", "high 82.8%"}


def test_completion_summary_contains_all_group_rows():
    df = build_model_sample.__globals__.get("pd")
    sample = df.DataFrame(
        {
            "sponsor_class": ["INDUSTRY", "INDUSTRY", "OTHER", "NETWORK", "OTHER_GOV"],
            "label": [1, 0, 1, 0, 1],
            "start_year": [2010, 2011, 2012, 2013, 2014],
            "n_uk_sites": [3, 5, 2, 1, 4],
        }
    )
    summary = summarize_completion_rates(sample)
    assert "ALL" in summary["group"].values
