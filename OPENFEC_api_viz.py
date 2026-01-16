import requests
import pandas as pd
import dpf  # your personal data pipeline functions

#$#
# Description: An interactive tool to explore FEC campaign finance data via their API.
#$#

# === CONFIG ===
API_KEY = "BGOI53H95vQ9k0qFNKj1mcVYwyhaji34iWn9WoRi"  # Need to hide this! FIX IT
BASE_URL = "https://api.open.fec.gov/v1"

def search_committees(): 
    """Interactive search for committees/candidates"""
    print("\n=== Search FEC Committees ===\n")
    query = input("Enter candidate or committee name (e.g., Ilhan Omar, Trump, Biden): ").strip()
    if not query:
        print("No query entered.")
        return None
# === SEARCH REQUEST ===
    url = f"{BASE_URL}/committees/"
    params = {
        "api_key": API_KEY,
        "q": query.upper(),
        "per_page": 50
    }
# === API REQUEST ===
    print(f"\nSearching for '{query}'...")
    r = requests.get(url, params=params)
    if r.status_code != 200:
        print(f"API Error: {r.status_code} - {r.text}")
        return None
# === PROCESS RESULTS ===
    results = r.json()["results"]
    if not results:
        print("No committees found.")
        return None
# === DISPLAY RESULTS ===
    df = pd.DataFrame(results)
    display_cols = ["committee_id", "name", "candidate_ids", "party", "state", "committee_type"]
    print("\nFound committees:")
    print(df[display_cols].to_string(index=False))

    # Let user pick one
    choice = input("\nEnter the committee_id you want to investigate (or press Enter to cancel): ").strip()
    if not choice:
        return None
# === VALIDATE SELECTION ===
    selected = df[df["committee_id"] == choice]
    if selected.empty:
        print("Invalid committee_id.")
        return None
# === RETURN SELECTION ===
    print(f"\nSelected: {selected.iloc[0]['name']} ({choice})")
    return choice


def fetch_all_contributions(committee_id):
    """Paginate through all Schedule A contributions for a committee"""
    print(f"\nFetching ALL contributions for committee {committee_id}...")
    url = f"{BASE_URL}/schedules/schedule_a/"
    all_data = []
    page = 1

    while True:
        params = { #=== API PARAMETERS ===
            "api_key": API_KEY, 
            "committee_id": committee_id, 
            "per_page": 100,
            "page": page,
            "sort": "-contribution_receipt_date"  # newest first (optional)
        }
        r = requests.get(url, params=params) 
        if r.status_code != 200:
            print(f"Error on page {page}: {r.status_code} - {r.text}")
            break

        results = r.json()["results"] #=== EXTRACT RESULTS ===
        if not results:
            print(f"No more data (finished at page {page-1}).")
            break

        all_data.extend(results) #=== AGGREGATE DATA ===
        print(f"Fetched page {page} ({len(results)} records, total so far: {len(all_data)})")
        page += 1

    if not all_data: #=== NO DATA CHECK ===
        print("No contributions found.")
        return pd.DataFrame()

    df = pd.DataFrame(all_data) #=== CONVERT TO DATAFRAME ===
    print(f"\nSuccessfully fetched {len(df)} total contribution records.")
    return df


def clean_and_prepare(df_raw):
    """Use your dpf interactive tools to clean and transform"""
    print("\n=== Raw Data Preview ===")
    dpf.Check(df_raw)

    # Select most useful columns (customize as needed)
    useful_cols = [
        'contributor_name', 'contributor_city', 'contributor_state',
        'contributor_zip', 'contributor_employer', 'contributor_occupation',
        'contribution_receipt_amount', 'contribution_receipt_date',
        'contributor_id', 'memo_text'
    ]
    available = [col for col in useful_cols if col in df_raw.columns]
    df = df_raw[available].copy()

    # Basic fixes before interactive cleansing
    if 'contribution_receipt_date' in df.columns:
        df['contribution_receipt_date'] = pd.to_datetime(df['contribution_receipt_date'], errors='coerce')

    print("\n=== Starting Interactive Cleansing ===")
    df_clean = dpf.interactive_cleanse(df)

    print("\n=== Starting Interactive Transformation (optional) ===")
    transform_more = input("Run interactive transformation? (y/n, default n): ").strip().lower()
    if transform_more == 'y':
        df_final = dpf.interactive_transform(df_clean)
    else:
        df_final = df_clean.copy()

    print("\n=== Final Cleaned Data ===")
    dpf.Check(df_final)
    return df_final


def main(): # Main interactive function
    print("=== Interactive FEC Campaign Finance Explorer ===\n")
# === SEARCH FOR COMMITTEE ===
    committee_id = search_committees()
    if not committee_id:
        print("Goodbye!")
        return
# === FETCH ALL CONTRIBUTIONS ===
    df_raw = fetch_all_contributions(committee_id)
    if df_raw.empty:
        print("Nothing to save. Exiting.")
        return
# == CLEAN AND PREPARE DATA ===
    df_final = clean_and_prepare(df_raw)
# == SAVE RESULTS ===
    filename = f"fec_contributions_{committee_id}.csv"
    df_final.to_csv(filename, index=False)
    print(f"\nSaved local copy: {filename}")

    # Save to MySQL
    save_to_db = input("\nSave this data to your MySQL 'main_db'? (y/n, default y): ").strip().lower()
    if save_to_db != 'n':
        table_name = input("Enter table name (default: fec_contributions): ").strip() or "fec_contributions"
        # Use your interactive MySQL function
        dpf.interactive_add_to_mysql(df_final)  # prompts for db/table/mode
    else:
        print("Not saving to database.")

    print("\nAll done! 🎉")

# === RUN MAIN FUNCTION ===
if __name__ == "__main__":
    main()