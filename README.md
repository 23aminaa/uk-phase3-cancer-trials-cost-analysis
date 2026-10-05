# Risk-adjusted cost of UK Phase 3 cancer trials

A reproducible analysis of how often UK Phase 3 cancer trials complete, whether registry data can predict completion, and what that implies for the risk-adjusted cost of taking a trial to completion.

## Project summary

This project studies UK-site Phase 3 cancer trials registered on ClinicalTrials.gov, using public registry fields to estimate:

- completion rates among UK Phase 3 cancer trials
- whether basic design variables predict completion
- how much stopped trials may already have spent
- the implied risk premium on top of a full trial budget

The output is a transparent, reproducible pipeline rather than a prediction model. The analysis uses a simple baseline because the registration-time covariates do not materially improve on the naive completion rate.

## Scope

- Data source: ClinicalTrials.gov API v2
- Trial filter: UK site, Phase 3, cancer condition
- Outcome: completed vs terminated/withdrawn
- Sample window: start years 2005 to 2019
- Exclusions: ongoing, suspended, and unknown-status trials are removed because their final state is not yet known

## Repository structure

```text
uk-phase3-cancer-trials-cost-analysis/
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── fetch_trials.py
│   ├── build_sample.py
│   ├── model.py
│   ├── cost_analysis.py
│   ├── reporting.py
│   └── run_pipeline.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── outputs/
├── notebooks/
│   └── exploratory_analysis.ipynb
├── tests/
│   └── test_pipeline.py
└── Makefile
```

## How to run

From the project root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.run_pipeline
```

This will:

1. fetch the raw ClinicalTrials.gov data
2. build the 2005–2019 UK sample
3. evaluate the baseline model
4. summarize completion rates
5. compute the risk premium grid
6. save outputs under `data/outputs/`

## Outputs

The pipeline creates the following files in `data/outputs/`:

- `model_metrics.csv`
- `completion_rate_summary.csv`
- `risk_premium_grid.csv`

## Key assumptions

The project intentionally keeps the cost layer simple and explicit:

- Cost inputs are placeholders, not published benchmarks
- Full cost is assumed to be:
  - 500 patients
  - £30,000 per patient
  - £2.5m set-up cost
- Set-up cost is treated as sunk when a trial stops
- A stopped trial is assumed to have spent the set-up cost plus a share of patient-related costs

These assumptions are defined in `src/config.py` so they can be revised without changing the analytical logic.

## Methods in brief

This project uses a simple logistic baseline trained on registry features such as:

- sponsor class
- randomisation
- masking
- number of arms
- intervention type
- cancer type
- number of countries

The notebook and pipeline show that these fields do not materially improve on a naive completion-rate baseline. This is the reason the project uses a base-rate approach for the risk-adjusted cost model.

## Notes

- This is a learning and portfolio project.
- It is not a prediction tool for assessing a specific trial.
- It is not advice on investment, pricing, or portfolio construction.
- The conclusions are intentionally limited to the defined sample: UK-site Phase 3 cancer trials, 2005–2019 starts.

## Reproducibility

The analysis is intentionally split into a small pipeline instead of one monolithic notebook. This makes it easier to:

- rerun exactly
- update assumptions cleanly
- audit the calculations
- explain the project to others

## Project status

The pipeline is structured to support both:

- exploratory analysis in a notebook
- reproducible production-style execution through scripts

This is a good foundation for a more polished portfolio piece or a future extension with sourced trial-cost benchmarks.
