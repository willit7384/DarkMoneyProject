import requests
import xml.etree.ElementTree as ET
import pandas as pd
import re
import time

SITEMAP_INDEX_URL = "https://www.propublica.org/sitemap.xml"
OUTPUT_CSV = "propublica_nonprofit_orgs_from_sitemap.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (nonprofit research)"
}

# -------------------------
# Helpers
# -------------------------
def strip_ns(elem):
    for el in elem.iter():
        if "}" in el.tag:
            el.tag = el.tag.split("}", 1)[1]
    return elem


def fetch_xml(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    root = ET.fromstring(r.content)
    return strip_ns(root)


EIN_PATTERN = re.compile(
    r"https://projects\.propublica\.org/nonprofits/organizations/(\d{9})"
)

# -------------------------
# Main scrape
# -------------------------
def scrape_nonprofit_eins_from_sitemap():
    print(f"🔍 Fetching sitemap index: {SITEMAP_INDEX_URL}")
    index_root = fetch_xml(SITEMAP_INDEX_URL)

    sitemap_urls = [
        loc.text for loc in index_root.findall(".//loc")
        if loc.text and "sitemap.xml?" in loc.text
    ]

    print(f"📄 Found {len(sitemap_urls)} daily sitemap files")

    rows = {}
    total_urls_scanned = 0

    for i, sitemap_url in enumerate(sitemap_urls, start=1):
        print(f"➡ [{i}/{len(sitemap_urls)}] {sitemap_url}")

        try:
            daily_root = fetch_xml(sitemap_url)

            for url_el in daily_root.findall(".//url"):
                loc = url_el.findtext("loc")
                total_urls_scanned += 1

                if not loc:
                    continue

                match = EIN_PATTERN.match(loc)
                if not match:
                    continue

                ein = match.group(1)

                # Deduplicate by EIN
                if ein not in rows:
                    rows[ein] = {
                        "ein": ein,
                        "organization_url": loc,
                        "source_sitemap": sitemap_url
                    }

            time.sleep(0.5)

        except Exception as e:
            print(f"⚠ Failed sitemap {sitemap_url}: {e}")

    df = pd.DataFrame(rows.values())
    df = df.sort_values("ein")

    df.to_csv(OUTPUT_CSV, index=False)

    print("\n✅ Sitemap scrape complete")
    print(f"URLs scanned: {total_urls_scanned}")
    print(f"Unique nonprofit orgs found: {len(df)}")
    print(f"Saved to: {OUTPUT_CSV}")

    return df


if __name__ == "__main__":
    scrape_nonprofit_eins_from_sitemap()
