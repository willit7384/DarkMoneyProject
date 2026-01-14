from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os

app = FastAPI(title="Dark Money API")

# ---- CORS (required for React) ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Database connection ----
def get_conn():
    return psycopg2.connect(
        host="localhost",
        database="nonprofit_990",
        user="postgres",
        password="OmniWolf42!",
        port=5432
    )

# ---- Health check ----
@app.get("/")
def root():
    return {"status": "ok"}

# ---- Donors endpoint ----
@app.get("/donors")
def get_donors():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            "organization" AS donor_name,
            SUM(CAST(NULLIF("amount", '') AS numeric)) AS total_grants,
            COUNT(*) AS grant_count
        FROM grants
        WHERE "tax_year" IS NOT NULL
        GROUP BY "organization"
        ORDER BY total_grants DESC
        LIMIT 10
    """)

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "donor_name": r[0],
            "grant_count": r[1],
            "total_grants": r[2]
        }
        for r in rows
    ]

# ---- Recipients endpoint ----
@app.get("/recipients")
def get_recipients():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        WITH donor_totals AS (
            SELECT
                "recipient",
                "organization",
                SUM(CAST(NULLIF("amount", '') AS numeric)) AS total_amount
            FROM grants
            WHERE "tax_year" IS NOT NULL
            GROUP BY "recipient", "organization"
        ),
        ranked_donors AS (
            SELECT
                "recipient",
                "organization" AS donor_name,
                total_amount,
                ROW_NUMBER() OVER (PARTITION BY "recipient" ORDER BY total_amount DESC) AS rank
            FROM donor_totals
        )
        SELECT
            "recipient" AS recipient_name,
            SUM(total_amount) AS total_grants,
            COUNT(*) AS grant_count,
            MAX(CASE WHEN rank = 1 THEN donor_name END) AS donor_name
        FROM ranked_donors
        GROUP BY "recipient"
        ORDER BY total_grants DESC
        LIMIT 10
    """)

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "recipient_name": r[0],
            "total_grants": r[1],
            "grant_count": r[2],
            "donor_name": r[3]
        }
        for r in rows
    ]
