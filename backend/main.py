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
def get_grants(min_amount: int = 0):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            organization AS source_org,
            recipient    AS target_org,
            amount,
            tax_year
        FROM grants
        WHERE amount >= %s
        LIMIT 500
    """, (min_amount,))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "source_org": r[0],
            "target_org": r[1],
            "amount": r[2],
            "tax_year": r[3],
        }
        for r in rows
    ]
