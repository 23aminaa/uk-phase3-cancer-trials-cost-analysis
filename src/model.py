import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score


def build_model_features(df: pd.DataFrame) -> pd.DataFrame:
    """Engineer the simple design-time features used in the baseline model."""
    conditions = df["conditions"].str.lower().fillna("")
    intervention_types = df["intervention_types"].fillna("")

    features = pd.DataFrame(
        {
            "industry": (df["sponsor_class"] == "INDUSTRY").astype(int),
            "randomised": (df["allocation"] == "RANDOMIZED").astype(int),
            "blinded": (df["masking"].notna() & (df["masking"] != "NONE")).astype(int),
            "three_plus_arms": (df["n_arms"] >= 3).astype(int),
            "biological": intervention_types.str.contains("BIOLOGICAL").astype(int),
            "log_countries": np.log1p(df["n_countries"]),
            "breast": conditions.str.contains("breast").astype(int),
            "lung": conditions.str.contains("lung").astype(int),
            "prostate": conditions.str.contains("prostate").astype(int),
            "colorectal": conditions.str.contains("colorectal|colon|rectal").astype(int),
            "blood_cancer": conditions.str.contains("leuk|lymphom|myelom").astype(int),
        }
    )
    return features


def evaluate_model(df: pd.DataFrame) -> tuple[LogisticRegression, dict]:
    """Train a simple baseline and report discrimination and calibration metrics."""
    X = build_model_features(df)
    y = df["label"].astype(int)

    train_mask = df["start_year"] <= 2014
    test_mask = df["start_year"] >= 2015

    model = LogisticRegression(max_iter=1000, C=0.5)
    model.fit(X[train_mask], y[train_mask])

    predicted_prob = model.predict_proba(X[test_mask])[:, 1]
    actual = y[test_mask].values
    baseline = y[train_mask].mean()

    metrics = {
        "auc": float(roc_auc_score(actual, predicted_prob)),
        "brier_model": float(brier_score_loss(actual, predicted_prob)),
        "brier_baseline": float(brier_score_loss(actual, np.full(len(actual), baseline))),
        "train_n": int(train_mask.sum()),
        "test_n": int(test_mask.sum()),
        "model_coefficients": pd.Series(model.coef_[0], index=X.columns).round(2).to_dict(),
    }

    return model, metrics


def main() -> None:
    df = pd.read_csv("data/processed/uk_phase3_cancer_model_sample.csv")
    _, metrics = evaluate_model(df)
    print(metrics)


if __name__ == "__main__":
    main()
