import os
import time
import requests
import pandas as pd
import dpf

# ================= CONFIG =================

API_KEY = os.getenv("OPENFEC_API_KEY") or "PUT_YOUR_KEY_IN_ENV"
BASE_URL = "https://api.open.fec.gov/v1"

INPUT_COMMITTEES = "fec_committees.txt"   # one committee_id per line
CHECKPOINT_FILE = "fec_completed_committees.txt"

PER_PAGE = 100
SLEEP_SECONDS = 0.5

HEADERS = {
    "User-Agent": "DarkMoneyProject/1.0 (research)"
}

session = requests.Session()
session.headers.update(HEADERS)

# ================= UTILS =================

def load_list(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [line.strip() for line in f if line.strip()]

def load_completed():
    return set(load_list(CHECKPOINT_FILE))

def mark_completed(committee_id):
    with open(CHECKPOINT_FILE, "a") as f:
        f.write(f"{committee_id}\n")

# ================= FETCH CONTRIBUTIONS =================

def fetch_all_contributions(committee_id):
    print(f"\n📥 Fetching contributions for {committee_id}")

    all_rows = []
    page = 1

    while True:
        params = {
            "api_key": API_KEY,
            "committee_id": committee_id,
            "per_page": PER_PAGE,
            "page": page,
            "sort": "-contribution_receipt_date"
        }

        r = session.get(
            f"{BASE_URL}/schedules/schedule_a/",
            params=params,
            timeout=20
        )

        if r.status_code != 200:
            print(f"⚠ API error on page {page}: {r.text}")
            break

        data = r.json()
        results = data.get("results", [])

        if not results:
            break

        all_rows.extend(results)
        print(f"  page {page}: {len(results)} records")
        page += 1
        time.sleep(SLEEP_SECONDS)

    print(f"✅ Total records: {len(all_rows)}")
    return pd.DataFrame(all_rows)

# ================= NORMALIZATION =================

def normalize_contributions(df, committee_id):
    if df.empty:
        return df

    keep = [
        "contributor_name",
        "contributor_city",
        "contributor_state",
        "contributor_zip",
        "contributor_employer",
        "contributor_occupation",
        "contribution_receipt_amount",
        "contribution_receipt_date",
        "contributor_id",
        "memo_text",
        "line_number",
        "report_type"
    ]

    cols = [c for c in keep if c in df.columns]
    out = df[cols].copy()

    out["committee_id"] = committee_id

    out["contribution_receipt_date"] = pd.to_datetime(
        out["contribution_receipt_date"],
        errors="coerce"
    )

    return out

# ================= MAIN PIPELINE =================

def main():
    committees = load_list(INPUT_COMMITTEES)
    completed = load_completed()

    if not committees:
        print("No committee IDs provided.")
        return

    engine = dpf.create_postgres_db()

    for i, committee_id in enumerate(committees, 1):
        if committee_id in completed:
            continue

        print(f"\n[{i}/{len(committees)}] Committee {committee_id}")

        raw = fetch_all_contributions(committee_id)
        if raw.empty:
            mark_completed(committee_id)
            continue

        df = normalize_contributions(raw, committee_id)

        dpf.add_dataframe_to_postgres(
            df,
            engine,
            table_name="fec_contributions",
            if_exists="append"  # ideally UPSERT on (committee_id, contributor_id, date, amount)
        )

        mark_completed(committee_id)

    print("\n✅ FEC ingestion complete")

if __name__ == "__main__":
    main()
