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

# ---- Grants endpoint ----
@app.get("/grants")
def get_grants():
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
    """)

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "donor_name": r[0],
            "total_grants": float(r[1]),
            "grant_count": r[2]
        }
        for r in rows
    ]
