import json
from pathlib import Path

import pandas as pd
import requests

from src.config import (
    CONDITION_FILTER,
    COUNTRY_FILTER,
    PHASE_FILTER,
    RAW_DIR,
)

URL = "https://clinicaltrials.gov/api/v2/studies"


def fetch_all_trials() -> pd.DataFrame:
    """Download all relevant Phase 3 cancer trials with a UK site."""
    params = {
        "query.locn": COUNTRY_FILTER,
        "query.cond": CONDITION_FILTER,
        "filter.advanced": f"AREA[Phase]{PHASE_FILTER}",
        "pageSize": 200,
    }

    rows = []
    page = 0

    while True:
        response = requests.get(URL, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()
        studies = data.get("studies", [])

        for study in studies:
            protocol = study.get("protocolSection", {})
            status_module = protocol.get("statusModule", {})
            design_module = protocol.get("designModule", {})
            design_info = design_module.get("designInfo", {})
            arms_module = protocol.get("armsInterventionsModule", {})
            sponsor_module = protocol.get("sponsorCollaboratorsModule", {})
            locations = protocol.get("contactsLocationsModule", {}).get("locations", [])

            rows.append(
                {
                    "nct_id": protocol.get("identificationModule", {}).get("nctId"),
                    "status": status_module.get("overallStatus"),
                    "start": status_module.get("startDateStruct", {}).get("date"),
                    "sponsor_class": sponsor_module.get("leadSponsor", {}).get("class"),
                    "allocation": design_info.get("allocation"),
                    "masking": design_info.get("maskingInfo", {}).get("masking"),
                    "n_arms": len(arms_module.get("armGroups", [])),
                    "intervention_types": ",".join(
                        sorted(
                            {
                                intervention.get("type")
                                for intervention in arms_module.get("interventions", [])
                                if intervention.get("type")
                            }
                        )
                    ),
                    "conditions": "; ".join(protocol.get("conditionsModule", {}).get("conditions", [])),
                    "n_countries": len({loc.get("country") for loc in locations if loc.get("country")}),
                    "n_uk_sites": sum(1 for loc in locations if loc.get("country") == "United Kingdom"),
                }
            )

        page += 1
        print(f"page {page}: collected {len(rows)} records")

        next_token = data.get("nextPageToken")
        if not next_token:
            break
        params["pageToken"] = next_token

    df = pd.DataFrame(rows)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(RAW_DIR / "clinicaltrials_raw.csv", index=False)
    return df


def main() -> None:
    fetch_all_trials()


if __name__ == "__main__":
    main()
