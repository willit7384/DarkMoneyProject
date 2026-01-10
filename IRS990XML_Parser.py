import os
import re
import xml.etree.ElementTree as ET
import pandas as pd
import dpf
import time

# ================= CONFIG =================

XML_FOLDER = "propublica_xml"
CSV_FOLDER = "IRS990CSV_Folder"
CHECKPOINT_FILE = "parsed_xml_files.txt"

os.makedirs(CSV_FOLDER, exist_ok=True)

# ================= DATA CONTAINERS =================

foundations = []
grants = []
officers = []
investments = []
asset_sales = []
assets = []

# ================= HELPERS =================

def strip_ns(elem):
    for el in elem.iter():
        if "}" in el.tag:
            el.tag = el.tag.split("}", 1)[1]
    return elem

def load_parsed_files():
    if not os.path.exists(CHECKPOINT_FILE):
        return set()
    with open(CHECKPOINT_FILE) as f:
        return set(line.strip() for line in f)

def mark_parsed(path):
    with open(CHECKPOINT_FILE, "a") as f:
        f.write(path + "\n")

def parse_filename_metadata(filename):
    """
    Expected format:
    EIN_FORMTYPE_YEAR_OBJECTID.xml
    """
    m = re.match(r"(\d+)_([A-Z0-9]+)_(\d{4}|unknown)_", filename)
    if not m:
        return None, None, None
    return m.group(1), m.group(2), m.group(3)

# ================= PARSER =================

parsed_files = load_parsed_files()
xml_count = 0
total_xml_files = sum(
    1
    for _r, _d, fs in os.walk(XML_FOLDER)
    for f in fs
    if f.lower().endswith(".xml") and os.path.join(_r, f) not in parsed_files
)
print(f"Found {total_xml_files} XML files to process (skipping {len(parsed_files)} already parsed)")
start_time = time.time()

for root_dir, _, files in os.walk(XML_FOLDER):
    for filename in files:
        if not filename.lower().endswith(".xml"):
            continue

        file_path = os.path.join(root_dir, filename)
        if file_path in parsed_files:
            continue

        xml_count += 1
        # progress info: count, percent, rate, ETA
        if total_xml_files:
            elapsed = time.time() - start_time
            pct = (xml_count / total_xml_files) * 100
            rate = (xml_count / elapsed) if elapsed > 0 else 0
            remaining = max(0, total_xml_files - xml_count)
            eta = (remaining / rate) if rate > 0 else None
            eta_str = f" ETA {eta:.1f}s" if eta is not None else ""
            print(f"Parsing {xml_count}/{total_xml_files} ({pct:.1f}%): {file_path} | {elapsed:.1f}s elapsed | {rate:.2f} f/s{eta_str}")
        else:
            print(f"Parsing {xml_count}: {file_path}")
        try:
            tree = ET.parse(file_path)
            root = strip_ns(tree.getroot())

            ein, form_type, year_from_name = parse_filename_metadata(filename)

            ein = ein or root.findtext(".//Filer/EIN")
            org = root.findtext(".//Filer/BusinessName/BusinessNameLine1Txt")
            tax_year = root.findtext(".//TaxYr") or year_from_name

            # ---------- FOUNDATION ----------
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

            # # Adding to your existing code

            # # ---------- SCHEDULE A ----------
            # for a in root.findall(".//IRS990ScheduleA"):
            #     foundations.append({
            #         "ein": ein,
            #         "organization": org,
            #         "public_support_total": a.findtext("PublicSupportTotal170Amt"),
            #         "total_gifts": a.findtext(".//TotalAmt"),
            #         "current_year_gifts": a.findtext(".//CurrentTaxYearAmt"),
            #         "gross_investment_income": a.findtext(".//GrossInvestmentIncome170Grp/TotalAmt"),
            #         "tax_year": tax_year,
            #         "source_file": filename
            #     })

            # # ---------- SCHEDULE B ----------
            # for b in root.findall(".//IRS990ScheduleB"):
            #     contributors = b.findall(".//ContributorInformationGrp")
            #     for c in contributors:
            #         # Check for restricted info if necessary
            #         if c.findtext("ContributorNum") != "RESTRICTED":
            #             grants.append({
            #                 "ein": ein,
            #                 "organization": org,
            #                 "contributor": c.findtext("ContributorBusinessName/BusinessNameLine1"),
            #                 "total_contributions": c.findtext("TotalContributionsAmt"),
            #                 "tax_year": tax_year,
            #                 "source_file": filename
            #             })

            # # ---------- SCHEDULE D ----------
            # for d in root.findall(".//IRS990ScheduleD"):
            #     assets.append({
            #         "ein": ein,
            #         "organization": org,
            #         "total_assets": d.findtext("TotalBookValueLandBuildingsAmt"),
            #         "total_revenue": d.findtext("TotalRevenuePerForm990Amt"),
            #         "total_expenses": d.findtext("TotExpnsEtcAuditedFinclStmtAmt"),
            #         "tax_year": tax_year,
            #         "source_file": filename
            #     })

            # # ---------- SCHEDULE I ----------
            # for i in root.findall(".//IRS990ScheduleI"):
            #     recipient_data = i.findall(".//RecipientTable")
            #     for r in recipient_data:
            #         grants.append({
            #             "ein": ein,
            #             "organization": org,
            #             "recipient": r.findtext("RecipientBusinessName/BusinessNameLine1Txt"),
            #             "grant_amount": r.findtext("CashGrantAmt"),
            #             "purpose": r.findtext("PurposeOfGrantTxt"),
            #             "tax_year": tax_year,
            #             "source_file": filename
            #         })

            mark_parsed(file_path)

        except Exception as e:
            print(f"[ERROR] {file_path}: {e}")

# ================= DATAFRAMES =================

dfs = {
    "foundations": pd.DataFrame(foundations),
    "grants": pd.DataFrame(grants),
    "officers": pd.DataFrame(officers),
    "investments": pd.DataFrame(investments),
    "asset_sales": pd.DataFrame(asset_sales)
    ,"assets": pd.DataFrame(assets)
}

# ================= POSTGRES LOAD =================

if __name__ == "__main__":
    engine = dpf.create_postgres_db()

    for table, df in dfs.items():
        if df.empty:
            continue
        dpf.add_dataframe_to_postgres(
            df,
            engine,
            table,
            if_exists="append",  # ideally UPSERT in dpf
        )

    print("\n=== PARSING COMPLETE ===")
    print(f"XML files parsed: {xml_count}")
