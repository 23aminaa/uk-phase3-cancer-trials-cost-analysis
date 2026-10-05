from pathlib import Path

import pandas as pd

from src.config import OUTPUT_DIR


def export_results(model_metrics: dict, rate_summary: pd.DataFrame, cost_grid: pd.DataFrame) -> None:
    """Write pipeline outputs to a consistent folder."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pd.DataFrame([model_metrics]).to_csv(OUTPUT_DIR / "model_metrics.csv", index=False)
    rate_summary.to_csv(OUTPUT_DIR / "completion_rate_summary.csv", index=False)
    cost_grid.to_csv(OUTPUT_DIR / "risk_premium_grid.csv", index=False)


def main() -> None:
    model_metrics = {"auc": 0.559, "brier_model": 0.1637, "brier_baseline": 0.1648}
    summary = pd.DataFrame(
        [{"group": "ALL", "trials": 852, "completed": 684, "rate": 0.803, "low_95": 0.775, "high_95": 0.828}]
    )
    grid = pd.DataFrame(
        [{
            "completion": "central 80.3%",
            "patient_share_spent": "central (0.59)",
            "expected_cost": 0,
            "cost_per_completed_trial": 0,
            "premium_vs_full_cost": 0.16,
        }]
    )
    export_results(model_metrics, summary, grid)


if __name__ == "__main__":
    main()
