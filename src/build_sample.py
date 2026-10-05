import pandas as pd

from src.config import PROCESSED_DIR, RAW_DIR, START_YEAR_MAX, START_YEAR_MIN


def build_model_sample(raw_df: pd.DataFrame | None = None, raw_path: str | None = None) -> pd.DataFrame:
    """Create the final model sample restricted to valid status, UK sites, and time window."""
    if raw_df is None:
        if raw_path is None:
            raw_path = RAW_DIR / "clinicaltrials_raw.csv"
        raw_df = pd.read_csv(raw_path)

    df = raw_df.copy()
    df["start"] = pd.to_datetime(df["start"], errors="coerce")
    df["label"] = df["status"].map({"COMPLETED": 1, "TERMINATED": 0, "WITHDRAWN": 0})
    df["start_year"] = df["start"].dt.year

    sample = df.dropna(subset=["label", "start_year"]).copy()
    sample = sample[
        (sample["n_uk_sites"] > 0)
        & (sample["start_year"] >= START_YEAR_MIN)
        & (sample["start_year"] <= START_YEAR_MAX)
    ].copy()

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    sample.to_csv(PROCESSED_DIR / "uk_phase3_cancer_model_sample.csv", index=False)
    return sample


def main() -> None:
    df = pd.read_csv(RAW_DIR / "clinicaltrials_raw.csv")
    build_model_sample(raw_df=df)


if __name__ == "__main__":
    main()
