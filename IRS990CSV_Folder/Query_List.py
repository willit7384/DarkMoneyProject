import pandas as pd

# Load CSV
df = pd.read_csv("IRS990CSV_Folder\grants.csv")

# Extract Recipient column, drop blanks, dedupe
org_names = (
    df["Recipient"]
    .dropna()
    .astype(str)
    .str.strip()
    .drop_duplicates()
)

# Save to txt
with open("org_names.txt", "w", encoding="utf-8") as f:
    for name in org_names:
        f.write(name + "\n")

print(f"✅ Saved {len(org_names)} organization names to org_names.txt")
