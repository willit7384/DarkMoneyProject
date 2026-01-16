import os
import re
import xml.etree.ElementTree as ET
import pandas as pd
import dpf
import time

# ================= CONFIG =================

# ================ PATHS =================
XML_FOLDER = "propublica_xml"
CSV_FOLDER = "IRS990CSV_Folder"
CHECKPOINT_FILE = "parsed_xml_files.txt"
# Create CSV folder if it doesn't exist
os.makedirs(CSV_FOLDER, exist_ok=True)

# ================= DATA CONTAINERS =================
# Initialize lists to hold parsed data
foundations = []
grants = []
officers = []
investments = []
asset_sales = []

# ================= HELPERS =================
# Function to strip namespaces from XML elements
def strip_ns(elem):
    for el in elem.iter():
        if "}" in el.tag:
            el.tag = el.tag.split("}", 1)[1]
    return elem
# Function to load already parsed files from checkpoint
def load_parsed_files():
    if not os.path.exists(CHECKPOINT_FILE):
        return set()
    with open(CHECKPOINT_FILE) as f:
        return set(line.strip() for line in f)
# Function to mark a file as parsed
def mark_parsed(path):
    with open(CHECKPOINT_FILE, "a") as f:
        f.write(path + "\n")
# Function to parse metadata from filename
def parse_filename_metadata(filename):
    """
    Expected format:
    EIN_FORMTYPE_YEAR_OBJECTID.xml
    """
    # Extract EIN, form type, and year using regex
    m = re.match(r"(\d+)_([A-Z0-9]+)_(\d{4}|unknown)_", filename)
    if not m:
        return None, None, None
    return m.group(1), m.group(2), m.group(3)
    # Return EIN, form type, year
# ================= PARSER =================

parsed_files = load_parsed_files()
xml_count = 0
# Count total XML files to left to process
total_xml_files = sum(
    1
    for _r, _d, fs in os.walk(XML_FOLDER) # traverses directory
    for f in fs # iterates through files
    if f.lower().endswith(".xml") and os.path.join(_r, f) not in parsed_files # filters out previously parsed XML files
)
print(f"Found {total_xml_files} XML files to process (skipping {len(parsed_files)} already parsed)")
start_time = time.time()
# Main parsing loop iterating through all files in XML_FOLDER
for root_dir, _, files in os.walk(XML_FOLDER):
    for filename in files:
        if not filename.lower().endswith(".xml"):
            continue
        # Skips already parsed XML files
        file_path = os.path.join(root_dir, filename)
        if file_path in parsed_files:
            continue

        xml_count += 1
        # Displays progress info: count, percent, rate, ETA during parsing process
        if total_xml_files:
            elapsed = time.time() - start_time
            pct = (xml_count / total_xml_files) * 100 # percentage
            rate = (xml_count / elapsed) if elapsed > 0 else 0 # files per second
            remaining = max(0, total_xml_files - xml_count) # files left
            eta = (remaining / rate) if rate > 0 else None # estimated time remaining
            eta_str = f" ETA {eta:.1f}s" if eta is not None else "" # format ETA
            print(f"Parsing {xml_count}/{total_xml_files} ({pct:.1f}%): {file_path} | {elapsed:.1f}s elapsed | {rate:.2f} f/s{eta_str}") # detailed progress
        else:
            print(f"Parsing {xml_count}: {file_path}") # print this if no total count available
        try: # XML parsing and data extraction
            tree = ET.parse(file_path)
            root = strip_ns(tree.getroot())
            # Extract metadata from filename
            ein, form_type, year_from_name = parse_filename_metadata(filename)
            # Fallbacks if EIN or year missing in XML
            ein = ein or root.findtext(".//Filer/EIN")
            org = root.findtext(".//Filer/BusinessName/BusinessNameLine1Txt")
            tax_year = root.findtext(".//TaxYr") or year_from_name

            # ---------- FOUNDATION ----------
            # Adding foundation table data
            foundations.append({
                "ein": ein,
                "organization": org,
                "tax_year": tax_year,
                "form_type": form_type,
                "total_revenue": root.findtext(".//TotalRevAndExpnssAmt"),
                "admin_expense": root.findtext(".//OtherExpensesRevAndExpnssAmt"),
                "source_file": filename
            })

            # ---------- GRANTS ----------
            # Adding grants table data
            for g in root.findall(".//GrantOrContributionPdDurYrGrp"):
                grants.append({
                    "ein": ein,
                    "organization": org,
                    "recipient": g.findtext("RecipientBusinessName/BusinessNameLine1Txt"),
                    "purpose": g.findtext("GrantOrContributionPurposeTxt"),
                    "amount": g.findtext("Amt"),
                    "tax_year": tax_year,
                    "source_file": filename
                })

            # ---------- OFFICERS ----------
            # Adding officers table data
            for o in root.findall(".//OfficerDirTrstKeyEmplGrp"):
                officers.append({
                    "ein": ein,
                    "organization": org,
                    "name": o.findtext("PersonNm"),
                    "title": o.findtext("TitleTxt"),
                    "hours_per_week": o.findtext("AverageHrsPerWkDevotedToPosRt"),
                    "compensation": o.findtext("CompensationAmt"),
                    "benefits": o.findtext("EmployeeBenefitProgramAmt"),
                    "tax_year": tax_year,
                    "source_file": filename
                })

            # ---------- INVESTMENTS ----------
            # Adding investments table data
            for tag, label in [
                ("InvestmentsCorporateStockGrp", "Corporate Stock"),
                ("InvestmentsCorporateBondsGrp", "Corporate Bond"),
                ("InvestmentsOtherGrp", "Other")
            ]:
                for inv in root.findall(f".//{tag}"):
                    investments.append({
                        "ein": ein,
                        "organization": org,
                        "investment_type": label,
                        "name": inv.findtext("StockNm") or inv.findtext("BondNm") or inv.findtext("CategoryOrItemTxt"),
                        "book_value": inv.findtext("BookValueAmt") or inv.findtext("EOYBookValueAmt"),
                        "market_value": inv.findtext("EOYFMVAmt"),
                        "source_file": filename
                    })

            # ---------- ASSET SALES ----------
            # Adding asset sales table data
            for s in root.findall(".//GainLossSaleOtherAssetGrp"):
                asset_sales.append({
                    "ein": ein,
                    "organization": org,
                    "asset": s.findtext("AssetDesc"),
                    "how_acquired": s.findtext("HowAcquiredTxt"),
                    "gross_sales_price": s.findtext("GrossSalesPriceAmt"),
                    "basis": s.findtext("BasisAmt"),
                    "net_gain_loss": s.findtext("TotalNetAmt"),
                    "source_file": filename
                })
            # Mark file as parsed in checkpoint
            mark_parsed(file_path)

        except Exception as e: # Log errors but continue processing
            print(f"[ERROR] {file_path}: {e}")
            
# ================= DATAFRAMES =================
# Convert lists to pandas DataFrames
dfs = {
    "foundations": pd.DataFrame(foundations),
    "grants": pd.DataFrame(grants),
    "officers": pd.DataFrame(officers),
    "investments": pd.DataFrame(investments),
    "asset_sales": pd.DataFrame(asset_sales)
}

# ================= POSTGRES LOAD =================
# Load data into PostgreSQL using dpf module
if __name__ == "__main__":
    engine = dpf.create_postgres_db()
# Load each DataFrame into its respective table
    for table, df in dfs.items():
        if df.empty:
            continue
        dpf.add_dataframe_to_postgres(
            df,
            engine,
            table,
            if_exists="append",  # ideally UPSERT in dpf
        )
#  Final summary printout
    print("\n=== PARSING COMPLETE ===")
    print(f"XML files parsed: {xml_count}")
