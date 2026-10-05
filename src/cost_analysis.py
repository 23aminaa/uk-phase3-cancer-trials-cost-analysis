import pandas as pd

from src.config import FULL_COST, SETUP_COST


def wilson_interval(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Return a Wilson score confidence interval for a proportion."""
    if n == 0:
        return float("nan"), float("nan")

    p = k / n
    d = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / d
    half = z * ((p * (1 - p) / n + z**2 / (4 * n**2)) ** 0.5) / d
    return centre - half, centre + half


def summarize_completion_rates(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize completion rates for all trials and sponsor groups."""
    rows = []
    df = df.copy()
    df["group"] = df["sponsor_class"].where(
        df["sponsor_class"].isin(["INDUSTRY", "OTHER", "NETWORK"]),
        "OTHER_GOV/NIH",
    )

    combined = [("ALL", df)] + list(df.groupby("group"))
    for name, group in combined:
        k = int(group["label"].sum())
        n = len(group)
        lo, hi = wilson_interval(k, n)
        rows.append(
            {
                "group": name,
                "trials": n,
                "completed": k,
                "rate": round(k / n, 3),
                "low_95": round(lo, 3),
                "high_95": round(hi, 3),
            }
        )

    return pd.DataFrame(rows)


def calculate_risk_premium_for_completion_rate(
    completion_rate: float,
    patient_share_spent: float,
    full_cost: float = FULL_COST,
) -> dict:
    """Compute expected cost and premium for a given completion rate and stop spend share."""
    # A stopped trial has sunk the setup cost, then spends a share of the patient cost component.
    patient_component = full_cost - SETUP_COST
    stopped_cost = SETUP_COST + patient_share_spent * patient_component

    expected_cost = completion_rate * full_cost + (1 - completion_rate) * stopped_cost
    cost_per_completion = expected_cost / completion_rate
    premium = (cost_per_completion / full_cost) - 1

    return {
        "expected_cost": expected_cost,
        "cost_per_completed_trial": cost_per_completion,
        "premium_vs_full_cost": premium,
    }


def build_cost_grid() -> pd.DataFrame:
    """Build the central sensitivity table for completion rate and stopped-trial spend share."""
    rates = {
        "low 77.5%": 0.775,
        "central 80.3%": 0.803,
        "high 82.8%": 0.828,
    }
    patient_share = {
        "low (0.20)": 0.20,
        "central (0.59)": 0.59,
        "high (1.00)": 1.00,
    }

    rows = []
    for rate_name, rate in rates.items():
        for share_name, share in patient_share.items():
            summary = calculate_risk_premium_for_completion_rate(rate, share)
            rows.append(
                {
                    "completion": rate_name,
                    "patient_share_spent": share_name,
                    "expected_cost": summary["expected_cost"],
                    "cost_per_completed_trial": summary["cost_per_completed_trial"],
                    "premium_vs_full_cost": summary["premium_vs_full_cost"],
                }
            )

    return pd.DataFrame(rows)


def main() -> None:
    df = pd.read_csv("data/processed/uk_phase3_cancer_model_sample.csv")
    summary = summarize_completion_rates(df)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
