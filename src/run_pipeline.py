import pandas as pd

from src.build_sample import build_model_sample
from src.config import RAW_DIR
from src.cost_analysis import build_cost_grid, summarize_completion_rates
from src.model import evaluate_model
from src.reporting import export_results


def run_pipeline() -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    """Run the full end-to-end analysis pipeline."""
    raw_df = pd.read_csv(RAW_DIR / "clinicaltrials_raw.csv")
    model_sample = build_model_sample(raw_df=raw_df)
    _, model_metrics = evaluate_model(model_sample)
    rate_summary = summarize_completion_rates(model_sample)
    cost_grid = build_cost_grid()
    export_results(model_metrics, rate_summary, cost_grid)

    return model_metrics, rate_summary, cost_grid


def main() -> None:
    metrics, summary, grid = run_pipeline()
    print("Model metrics:")
    print(metrics)
    print("\nCompletion-rate summary:")
    print(summary.to_string(index=False))
    print("\nRisk-premium grid:")
    print(grid.to_string(index=False))


if __name__ == "__main__":
    import sys
    from pathlib import Path

    if __package__ is None or __package__ == "":
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

    main()
