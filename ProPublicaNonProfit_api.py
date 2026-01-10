import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import time
import os
import csv
from urllib.parse import urljoin, urlparse, parse_qs

# =========================
# CONFIG
# =========================
BASE_URL = "https://projects.propublica.org/nonprofits/api/v2"
INPUT_CSV = "influencewatch_orgs.csv"
XML_OUTPUT_DIR = "propublica_xml"
IW_TEXT_DIR = "influencewatch_text"
CHECKPOINT_FILE = "completed_eins.txt"

HEADERS = {
    "User-Agent": "DarkMoneyProject/1.0 (research)"
}

session = requests.Session()
session.headers.update(HEADERS)

# =========================
# UTILS
# =========================
def load_completed_eins():
    if not os.path.exists(CHECKPOINT_FILE):
        return set()
    with open(CHECKPOINT_FILE) as f:
        return set(line.strip() for line in f if line.strip())

def mark_completed(ein):
    with open(CHECKPOINT_FILE, "a") as f:
        f.write(f"{ein}\n")

def force_string_ids(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = df[c].astype(str)
    return df

# =========================
# PROPUBLICA ORG + FILINGS
# =========================
def get_org_details_and_filings(ein):
    url = f"{BASE_URL}/organizations/{ein}.json"
    r = session.get(url, timeout=15)

    if r.status_code != 200:
        print(f"⚠ ProPublica lookup failed for EIN {ein}")
        return None, None

    data = r.json()
    return data.get("organization", {}), data.get("have_filings", [])

# =========================
# XML SCRAPER
# =========================
def scrape_and_download_propublica_xml(ein):
    base_url = f"https://projects.propublica.org/nonprofits/organizations/{ein}"
    print(f"\n🔍 Scanning ProPublica page: {base_url}")

    r = session.get(base_url, timeout=15)
    if r.status_code != 200:
        print("⚠ Page not reachable")
        return []

    soup = BeautifulSoup(r.text, "html.parser")

    ein_dir = os.path.join(XML_OUTPUT_DIR, ein)
    os.makedirs(ein_dir, exist_ok=True)

    downloaded = []

    for section in soup.select("section.document-links"):
        form_tag = section.find("h5")
        form_type = (
            form_tag.get_text(strip=True)
            .replace(" ", "")
            .replace("-", "")
            if form_tag else "UNKNOWN"
        )

        year = "unknown"
        filed_on = section.find("span", class_="filed-on")
        if filed_on:
            m = re.search(r"(19|20)\d{2}", filed_on.get_text())
            if m:
                year = m.group(0)

        xml_btn = section.find(
            "a", class_="btn",
            string=lambda s: s and s.strip().upper() == "XML"
        )
        if not xml_btn:
            continue

        href = xml_btn.get("href")
        xml_url = urljoin("https://projects.propublica.org", href)

        parsed = urlparse(xml_url)
        object_id = parse_qs(parsed.query).get("object_id", ["unknown"])[0]

        filename = f"{ein}_{form_type}_{year}_{object_id}.xml"
        path = os.path.join(ein_dir, filename)

        if os.path.exists(path):
            continue

        try:
            print(f"⬇ {filename}")
            resp = session.get(xml_url, timeout=20)
            if resp.status_code == 200 and resp.content.strip():
                with open(path, "wb") as f:
                    f.write(resp.content)
                downloaded.append(path)
                time.sleep(1)
        except Exception as e:
            print(f"⚠ XML error: {e}")

    print(f"✅ {len(downloaded)} XML files downloaded")
    return downloaded

# =========================
# INFLUENCEWATCH NARRATIVE
# =========================
def scrape_influencewatch_text(slug, org_name):
    url = f"https://www.influencewatch.org/non-profit/{slug}"
    print(f"📝 Scraping InfluenceWatch: {url}")

    r = session.get(url, timeout=15)
    if r.status_code != 200:
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    content = soup.find("div", class_="profile-main-content the-content")
    if not content:
        return None

    blocks = []
    for el in content.find_all(["h2", "p"]):
        text = el.get_text(strip=True)
        if not text or text.lower().startswith("source"):
            continue
        blocks.append(f"\n## {text}" if el.name == "h2" else text)

    os.makedirs(IW_TEXT_DIR, exist_ok=True)
    path = os.path.join(IW_TEXT_DIR, f"{slug}_influencewatch.txt")

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"Organization: {org_name}\n")
        f.write("Source: InfluenceWatch\n\n")
        f.write("\n\n".join(blocks))

    return path

# =========================
# MAIN PIPELINE (EIN-FIRST)
# =========================
def main():
    completed = load_completed_eins()

    with open(INPUT_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for i, row in enumerate(reader, 1):
            ein = row["ein"]
            slug = row["slug"]
            org_name = row["org_name"]

            if ein in completed:
                continue

            print(f"\n📦 [{i}] Processing EIN {ein} — {org_name}")

            org, filings = get_org_details_and_filings(ein)
            if not org:
                continue

            scrape_and_download_propublica_xml(ein)
            scrape_influencewatch_text(slug, org_name)

            mark_completed(ein)
            time.sleep(2)

    print("\n✅ Batch complete")

if __name__ == "__main__":
    main()
