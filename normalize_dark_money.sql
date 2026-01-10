BEGIN;

-- Normalize dark money contributions by removing duplicates and standardizing formats
DROP VIEW IF EXISTS grant_edges;
DROP VIEW IF EXISTS org_financials;

DROP TABLE IF EXISTS asset_sales_normalized;
DROP TABLE IF EXISTS investments_normalized;
DROP TABLE IF EXISTS officers_normalized;
DROP TABLE IF EXISTS grants_normalized;
DROP TABLE IF EXISTS filings;
DROP TABLE IF EXISTS organizations;

-- Create normalized tables

-- Organizations table to store unique organizations
CREATE TABLE organizations (
    org_id SERIAL PRIMARY KEY,
    ein TEXT UNIQUE,
    name TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO organizations (ein, name)
SELECT DISTINCT ein, organization
FROM foundations
WHERE ein IS NOT NULL
ON CONFLICT (ein) DO NOTHING;

-- Filings table to store financial data

CREATE TABLE filings (
    filing_id SERIAL PRIMARY KEY,
    org_id INT REFERENCES organizations(org_id),
    tax_year INT,
    form_type TEXT,
    total_revenue NUMERIC,
    admin_expense NUMERIC,
    source_file TEXT,
    UNIQUE (org_id, tax_year, form_type)
);

INSERT INTO filings (
    org_id, tax_year, form_type,
    total_revenue, admin_expense, source_file
)
SELECT
    o.org_id,
    f.tax_year::INT,
    f.form_type,
    f.total_revenue::NUMERIC,
    f.admin_expense::NUMERIC,
    f.source_file
FROM foundations f
JOIN organizations o ON o.ein = f.ein
WHERE f.tax_year ~ '^\d{4}$'
ON CONFLICT DO NOTHING;

--MONEY FLOWS (GRANTS-MOST RELEVANT TO DARK MONEY)

CREATE TABLE grants_normalized (
    grant_id SERIAL PRIMARY KEY,
    source_org_id INT REFERENCES organizations(org_id),
    recipient_name TEXT,
    amount NUMERIC,
    tax_year INT,
    purpose TEXT,
    source_file TEXT
);

INSERT INTO grants_normalized (
    source_org_id,
    recipient_name,
    amount,
    tax_year,
    purpose,
    source_file
)
SELECT
    o.org_id,
    g.recipient,
    g.amount::NUMERIC,
    g.tax_year::INT,
    g.purpose,
    g.source_file
FROM grants g
JOIN organizations o ON o.ein = g.ein
WHERE g.amount IS NOT NULL;

--Officers table to store officer information

CREATE TABLE officers_normalized (
    officer_id SERIAL PRIMARY KEY,
    org_id INT REFERENCES organizations(org_id),
    name TEXT,
    title TEXT,
    hours_per_week NUMERIC,
    compensation NUMERIC,
    benefits NUMERIC,
    tax_year INT
);

INSERT INTO officers_normalized (
    org_id, name, title,
    hours_per_week, compensation, benefits, tax_year
)
SELECT
    o.org_id,
    off.name,
    off.title,
    off.hours_per_week::NUMERIC,
    off.compensation::NUMERIC,
    off.benefits::NUMERIC,
    off.tax_year::INT
FROM officers off
JOIN organizations o ON o.ein = off.ein;

-- Investment table to store investment information

CREATE TABLE investments_normalized (
    investment_id SERIAL PRIMARY KEY,
    org_id INT REFERENCES organizations(org_id),
    investment_type TEXT,
    name TEXT,
    book_value NUMERIC,
    market_value NUMERIC
);

INSERT INTO investments_normalized (
    org_id, investment_type, name,
    book_value, market_value
)
SELECT
    o.org_id,
    i.investment_type,
    i.name,
    i.book_value::NUMERIC,
    i.market_value::NUMERIC
FROM investments i
JOIN organizations o ON o.ein = i.ein;

--Asset sales table to store asset sale information

CREATE TABLE asset_sales_normalized (
    sale_id SERIAL PRIMARY KEY,
    org_id INT REFERENCES organizations(org_id),
    asset TEXT,
    how_acquired TEXT,
    gross_sales_price NUMERIC,
    basis NUMERIC,
    net_gain_loss NUMERIC
);

INSERT INTO asset_sales_normalized (
    org_id, asset, how_acquired,
    gross_sales_price, basis, net_gain_loss
)
SELECT
    o.org_id,
    s.asset,
    s.how_acquired,
    s.gross_sales_price::NUMERIC,
    s.basis::NUMERIC,
    s.net_gain_loss::NUMERIC
FROM asset_sales s
JOIN organizations o ON o.ein = s.ein;

--INDEXES FOR PERFORMANCE

CREATE INDEX idx_org_ein ON organizations(ein);
CREATE INDEX idx_filings_org_year ON filings(org_id, tax_year);
CREATE INDEX idx_grants_source ON grants_normalized(source_org_id);
CREATE INDEX idx_grants_year ON grants_normalized(tax_year);
CREATE INDEX idx_officers_org ON officers_normalized(org_id);

--ANALYSIS VIEWS

CREATE VIEW grant_edges AS
SELECT
    o.name AS source_org,
    g.recipient_name AS target_org,
    g.amount,
    g.tax_year,
    g.purpose
FROM grants_normalized g
JOIN organizations o ON o.org_id = g.source_org_id;

--ORG FINANCIAL SUMMARY VIEW

CREATE VIEW org_financials AS
SELECT
    o.name,
    f.tax_year,
    f.total_revenue,
    f.admin_expense,
    SUM(g.amount) AS total_granted
FROM filings f
JOIN organizations o ON o.org_id = f.org_id
LEFT JOIN grants_normalized g
    ON g.source_org_id = o.org_id
    AND g.tax_year = f.tax_year
GROUP BY o.name, f.tax_year, f.total_revenue, f.admin_expense;

--EXPORT NORMALIZED DATA

\copy (
    SELECT source_org, target_org, amount, tax_year
    FROM grant_edges
) TO 'C:/temp/grant_edges.csv' CSV HEADER;




COMMIT;
