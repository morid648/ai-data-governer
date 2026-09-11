-- ==============================================================================
-- AI Data Governor — Baseline Ground Truth Validation Queries (TASK-1.3)
-- ==============================================================================
-- These queries establish and verify the exact ground truth anomalies present
-- in the raw AtliQ dataset prior to multi-agent remediation.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. Missing / Blank Values
-- ------------------------------------------------------------------------------
SELECT 
    'dim_customer.customer' AS column_checked,
    COUNT(*) FILTER (WHERE customer IS NULL OR TRIM(customer) = '') AS missing_count
FROM dim_customer
UNION ALL
SELECT 
    'dim_customer.platform',
    COUNT(*) FILTER (WHERE platform IS NULL OR TRIM(platform) = '')
FROM dim_customer
UNION ALL
SELECT 
    'dim_market.sub_zone',
    COUNT(*) FILTER (WHERE sub_zone IS NULL OR TRIM(sub_zone) = '')
FROM dim_market
UNION ALL
SELECT 
    'dim_market.region',
    COUNT(*) FILTER (WHERE region IS NULL OR TRIM(region) = '')
FROM dim_market
UNION ALL
SELECT 
    'dim_product.category',
    COUNT(*) FILTER (WHERE category IS NULL OR TRIM(category) = '')
FROM dim_product
UNION ALL
SELECT 
    'dim_product.variant',
    COUNT(*) FILTER (WHERE variant IS NULL OR TRIM(variant) = '')
FROM dim_product;

-- ------------------------------------------------------------------------------
-- 2. Placeholder Tokens ("UNKNOWN", "-", "N/A")
-- ------------------------------------------------------------------------------
SELECT 
    'dim_customer.platform' AS column_checked,
    platform AS placeholder_value,
    COUNT(*) AS row_count
FROM dim_customer
WHERE platform IN ('UNKNOWN', '-', 'N/A')
GROUP BY platform
UNION ALL
SELECT 
    'dim_product.category',
    category,
    COUNT(*)
FROM dim_product
WHERE category IN ('UNKNOWN', '-', 'N/A')
GROUP BY category;

-- ------------------------------------------------------------------------------
-- 3. Mixed Types in Numeric Quantity Columns (Trailing 'units' text)
-- ------------------------------------------------------------------------------
SELECT 
    'fact_sales_monthly.sold_quantity' AS column_checked,
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE sold_quantity ~* '\s*units?') AS non_numeric_rows,
    ROUND(COUNT(*) FILTER (WHERE sold_quantity ~* '\s*units?')::numeric / COUNT(*) * 100, 2) AS percentage
FROM fact_sales_monthly
UNION ALL
SELECT 
    'fact_forecast_monthly.forecast_quantity',
    COUNT(*),
    COUNT(*) FILTER (WHERE forecast_quantity ~* '\s*units?'),
    ROUND(COUNT(*) FILTER (WHERE forecast_quantity ~* '\s*units?')::numeric / COUNT(*) * 100, 2)
FROM fact_forecast_monthly;

-- ------------------------------------------------------------------------------
-- 4. Inconsistent Naming, Casing, and Whitespace
-- ------------------------------------------------------------------------------
-- Trailing whitespace in customer names:
SELECT 
    customer,
    LENGTH(customer) AS raw_length,
    LENGTH(TRIM(customer)) AS trimmed_length,
    COUNT(*) AS occurrences
FROM dim_customer
WHERE customer <> TRIM(customer)
GROUP BY customer;

-- Casing inconsistencies (e.g. Atliq vs AltiQ):
SELECT 
    customer,
    COUNT(*) AS count
FROM dim_customer
WHERE LOWER(customer) LIKE '%atliq%' OR LOWER(customer) LIKE '%altiq%'
GROUP BY customer;

-- ------------------------------------------------------------------------------
-- 5. Referential Integrity Violations (Orphan FKs)
-- ------------------------------------------------------------------------------
-- Orphan customer_codes in fact_sales_monthly not in dim_customer:
SELECT 
    COUNT(DISTINCT f.customer_code) AS distinct_orphan_codes,
    COUNT(*) AS total_orphan_rows,
    COUNT(*) FILTER (WHERE f.customer_code ~ '^ZZZ\d+') AS zzz_placeholder_rows
FROM fact_sales_monthly f
LEFT JOIN dim_customer c ON f.customer_code = c.customer_code
WHERE c.customer_code IS NULL;

-- Missing markets in fact_sales_monthly not in dim_market:
SELECT 
    DISTINCT f.market AS missing_market_in_dim_market
FROM fact_sales_monthly f
LEFT JOIN dim_market m ON f.market = m.market
WHERE m.market IS NULL;

-- ------------------------------------------------------------------------------
-- 6. Duplicate Rows
-- ------------------------------------------------------------------------------
SELECT 'dim_customer' AS table_name, COUNT(*) - COUNT(DISTINCT customer_code) AS duplicate_key_count FROM dim_customer
UNION ALL
SELECT 'dim_product', COUNT(*) - COUNT(DISTINCT product_code) FROM dim_product;

-- Duplicate row combinations in fact_sales_monthly:
SELECT COUNT(*) AS duplicate_rows_in_sales
FROM (
    SELECT date, product_code, customer_code, market, COUNT(*)
    FROM fact_sales_monthly
    GROUP BY date, product_code, customer_code, market
    HAVING COUNT(*) > 1
) sub;

-- ------------------------------------------------------------------------------
-- 7. Missing Dimension Linkage
-- ------------------------------------------------------------------------------
SELECT 
    'fact_sales_monthly' AS table_name,
    COUNT(*) AS rows_with_code_but_null_name
FROM fact_sales_monthly
WHERE customer_code IS NOT NULL AND (customer_name IS NULL OR TRIM(customer_name) = '')
UNION ALL
SELECT 
    'fact_forecast_monthly',
    COUNT(*)
FROM fact_forecast_monthly
WHERE customer_code IS NOT NULL AND (customer_name IS NULL OR TRIM(customer_name) = '');
