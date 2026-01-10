from fastapi import FastAPI, Query
from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:password@localhost:5432/nonprofit_990"
)

engine = create_engine(DATABASE_URL)
app = FastAPI(title="Dark Money API")

# ---------- HEALTH ----------
@app.get("/")
def root():
    return {"status": "ok"}

# ---------- ORGS ----------
@app.get("/organizations")
def get_organizations(limit: int = 100):
    q = text("""
        SELECT * FROM api_organizations
        ORDER BY name
        LIMIT :limit
    """)
    with engine.connect() as conn:
        return conn.execute(q, {"limit": limit}).mappings().all()

# ---------- FILINGS ----------
@app.get("/filings/{ein}")
def get_filings(ein: str):
    q = text("""
        SELECT * FROM api_filings
        WHERE ein = :ein
        ORDER BY tax_year DESC
    """)
    with engine.connect() as conn:
        return conn.execute(q, {"ein": ein}).mappings().all()

# ---------- GRANTS (GRAPH) ----------
@app.get("/grants")
def get_grants(
    year: int | None = None,
    min_amount: float = 0
):
    sql = """
        SELECT * FROM api_grants
        WHERE amount >= :min_amount
    """
    params = {"min_amount": min_amount}

    if year:
        sql += " AND tax_year = :year"
        params["year"] = year

    with engine.connect() as conn:
        return conn.execute(text(sql), params).mappings().all()
