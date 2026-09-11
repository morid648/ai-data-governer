-- ==============================================================================
-- AI Data Governor — Target Schema DDL (TASK-1.1)
-- ==============================================================================
-- Intentionally created WITHOUT foreign key constraints so raw "dirty" data
-- loads without database-level rejection. The AI Data Governor agents will
-- inspect, surface, and audit referential integrity violations in Phase 3.
-- ==============================================================================

-- 1. Customer Dimension
DROP TABLE IF EXISTS dim_customer CASCADE;
CREATE TABLE dim_customer (
    customer        TEXT,
    market          TEXT,
    platform        TEXT,
    channel         TEXT,
    customer_code   TEXT PRIMARY KEY
);

-- 2. Market Dimension
DROP TABLE IF EXISTS dim_market CASCADE;
CREATE TABLE dim_market (
    market          TEXT PRIMARY KEY,
    sub_zone        TEXT,
    region          TEXT
);

-- 3. Product Dimension
DROP TABLE IF EXISTS dim_product CASCADE;
CREATE TABLE dim_product (
    product_code    TEXT PRIMARY KEY,
    division        TEXT,
    segment         TEXT,
    category        TEXT,
    product         TEXT,
    variant         TEXT
);

-- 4. Monthly Sales Fact
-- Note: sold_quantity is TEXT intentionally to accommodate dirty values like "9 units"
DROP TABLE IF EXISTS fact_sales_monthly CASCADE;
CREATE TABLE fact_sales_monthly (
    date            DATE,
    division        TEXT,
    category        TEXT,
    product_code    TEXT,
    product         TEXT,
    market          TEXT,
    platform        TEXT,
    channel         TEXT,
    customer_code   TEXT,
    customer_name   TEXT,
    sold_quantity   TEXT
);

-- 5. Monthly Forecast Fact
-- Note: forecast_quantity is TEXT intentionally to accommodate dirty values like "12 units"
DROP TABLE IF EXISTS fact_forecast_monthly CASCADE;
CREATE TABLE fact_forecast_monthly (
    date                DATE,
    division            TEXT,
    category            TEXT,
    product_code        TEXT,
    product             TEXT,
    market              TEXT,
    platform            TEXT,
    channel             TEXT,
    customer_code       TEXT,
    customer_name       TEXT,
    forecast_quantity   TEXT
);

-- Optional: Create indices for performance
CREATE INDEX IF NOT EXISTS idx_sales_cust_code ON fact_sales_monthly(customer_code);
CREATE INDEX IF NOT EXISTS idx_sales_prod_code ON fact_sales_monthly(product_code);
CREATE INDEX IF NOT EXISTS idx_sales_market ON fact_sales_monthly(market);

CREATE INDEX IF NOT EXISTS idx_forecast_cust_code ON fact_forecast_monthly(customer_code);
CREATE INDEX IF NOT EXISTS idx_forecast_prod_code ON fact_forecast_monthly(product_code);
CREATE INDEX IF NOT EXISTS idx_forecast_market ON fact_forecast_monthly(market);
