import requests
import re
import csv
import time
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

BASE_URL = "https://www.influencewatch.org"
OUTPUT_FILE = "influencewatch_orgs.csv"

HEADERS = {
    "User-Agent": "DarkMoneyProject/1.0 (research)"
}

EIN_REGEX = re.compile(r"\b\d{2}-\d{7}\b")

# -------------------------
# Sitemap parsing
# -------------------------

def fetch(url):
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.text

def parse_sitemap(xml_text):
    root = ET.fromstring(xml_text)
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    urls = []

    if root.tag.endswith("sitemapindex"):
        for sm in root.findall(f"{ns}sitemap"):
            loc = sm.find(f"{ns}loc").text
            urls.extend(parse_sitemap(fetch(loc)))
    else:
        for url in root.findall(f"{ns}url"):
            loc = url.find(f"{ns}loc").text
            urls.append(loc)

    return urls

# -------------------------
# InfluenceWatch org page parsing
# -------------------------

def extract_org_data(url):
    r = requests.get(url, headers=HEADERS, timeout=15)
    if r.status_code != 200:
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    ein_match = EIN_REGEX.search(text)
    if not ein_match:
        return None

    ein = ein_match.group()

    name_tag = soup.find("h1")
    org_name = name_tag.get_text(strip=True) if name_tag else None

    # Optional fields
    location = None
    subsection = None

    if "501(c)(4)" in text:
        subsection = "501(c)(4)"
    elif "501(c)(3)" in text:
        subsection = "501(c)(3)"

    return {
        "ein": ein,
        "org_name": org_name,
        "slug": url.rstrip("/").split("/")[-1],
        "location": location,
        "subsection": subsection
    }

# -------------------------
# Main pipeline
# -------------------------

def main():
    sitemap_url = f"{BASE_URL}/sitemap.xml"
    print("Fetching InfluenceWatch sitemap...")
    urls = parse_sitemap(fetch(sitemap_url))

    org_urls = [
        u for u in urls
        if "/non-profit/" in u
    ]

    print(f"Found {len(org_urls)} org pages")

    seen_eins = set()
    rows = []

    for i, url in enumerate(org_urls, 1):
        print(f"[{i}/{len(org_urls)}] {url}")
        try:
            data = extract_org_data(url)
            if not data:
                continue
            if data["ein"] in seen_eins:
                continue

            seen_eins.add(data["ein"])
            rows.append(data)
            time.sleep(2)

        except Exception as e:
            print(f"Error: {e}")

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["ein", "org_name", "slug", "location", "subsection"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved {len(rows)} organizations to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
