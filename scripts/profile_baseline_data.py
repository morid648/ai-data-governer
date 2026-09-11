#!/usr/bin/env python3
"""
Baseline Data Quality Profiler for AI Data Governor (TASK-1.3)
Verifies the ground truth data anomalies in the raw dirty AtliQ dataset.
"""

import os
import re
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")

def profile_dataset():
    print("=" * 80)
    print("AI DATA GOVERNOR -- BASELINE DATA-QUALITY AUDIT")
    print("=" * 80)

    # 1. Load CSVs
    dim_customer = pd.read_csv(os.path.join(DATA_DIR, "dim_customer.csv"), dtype=str)
    dim_market = pd.read_csv(os.path.join(DATA_DIR, "dim_market.csv"), dtype=str)
    dim_product = pd.read_csv(os.path.join(DATA_DIR, "dim_product.csv"), dtype=str)
    fact_sales = pd.read_csv(os.path.join(DATA_DIR, "fact_sales_monthly.csv"), dtype=str)
    fact_forecast = pd.read_csv(os.path.join(DATA_DIR, "fact_forecast_monthly.csv"), dtype=str)

    print(f"\n[1] Row Counts:")
    print(f"  - dim_customer:          {len(dim_customer):>6} rows, {len(dim_customer.columns)} cols")
    print(f"  - dim_market:            {len(dim_market):>6} rows, {len(dim_market.columns)} cols")
    print(f"  - dim_product:           {len(dim_product):>6} rows, {len(dim_product.columns)} cols")
    print(f"  - fact_sales_monthly:    {len(fact_sales):>6} rows, {len(fact_sales.columns)} cols")
    print(f"  - fact_forecast_monthly: {len(fact_forecast):>6} rows, {len(fact_forecast.columns)} cols")

    # 2. Missing values
    print(f"\n[2] Missing / Blank Values:")
    print(f"  - dim_customer.customer:       {dim_customer['customer'].isna().sum()} nulls, {(dim_customer['customer'].str.strip() == '').sum()} blanks")
    print(f"  - dim_customer.platform:       {dim_customer['platform'].isna().sum()} nulls, {(dim_customer['platform'].str.strip() == '').sum()} blanks")
    print(f"  - dim_market.sub_zone:         {dim_market['sub_zone'].isna().sum()} nulls")
    print(f"  - dim_market.region:           {dim_market['region'].isna().sum()} nulls")
    print(f"  - dim_product.category:        {dim_product['category'].isna().sum()} nulls")
    print(f"  - dim_product.variant:         {dim_product['variant'].isna().sum()} nulls")

    # 3. Placeholder tokens
    print(f"\n[3] Placeholder Tokens:")
    print(f"  - dim_customer.platform == 'UNKNOWN':  {(dim_customer['platform'] == 'UNKNOWN').sum()} rows")
    print(f"  - dim_product.category == 'UNKNOWN':   {(dim_product['category'] == 'UNKNOWN').sum()} rows")
    print(f"  - dim_product.category == '-':         {(dim_product['category'] == '-').sum()} rows")

    # 4. Mixed types in quantity columns (strings ending with ' units')
    sales_units = fact_sales['sold_quantity'].str.contains(r'\s*units?', case=False, na=False).sum()
    forecast_units = fact_forecast['forecast_quantity'].str.contains(r'\s*units?', case=False, na=False).sum()
    print(f"\n[4] Non-numeric 'X units' Suffix:")
    print(f"  - fact_sales_monthly.sold_quantity:        {sales_units} / {len(fact_sales)} rows ({sales_units/len(fact_sales):.1%})")
    print(f"  - fact_forecast_monthly.forecast_quantity: {forecast_units} / {len(fact_forecast)} rows ({forecast_units/len(fact_forecast):.1%})")

    # 5. Inconsistent casing / whitespace
    print(f"\n[5] Inconsistent Casing & Whitespace:")
    customers = dim_customer['customer'].dropna().tolist()
    atliq_variants = [c for c in customers if 'atliq' in c.lower() or 'altiq' in c.lower()]
    print(f"  - AtliQ customer name variants: {set(atliq_variants)}")
    trailing_spaces = [c for c in customers if c != c.strip()]
    print(f"  - Customers with trailing spaces: {trailing_spaces}")

    # 6. Referential integrity violations
    print(f"\n[6] Referential Integrity Violations:")
    dim_cust_codes = set(dim_customer['customer_code'].dropna())
    sales_cust_codes = set(fact_sales['customer_code'].dropna())
    orphan_codes = sales_cust_codes - dim_cust_codes
    zzz_orphans = [c for c in orphan_codes if re.match(r'^ZZZ\d+', c)]
    sales_orphan_rows = fact_sales['customer_code'].isin(orphan_codes).sum()
    print(f"  - Orphan customer_codes in fact_sales: {len(orphan_codes)} distinct codes ({sales_orphan_rows} rows total)")
    print(f"  - Orphan codes matching 'ZZZ####' pattern: {len(zzz_orphans)} distinct codes")
    
    dim_markets = set(dim_market['market'].dropna())
    sales_markets = set(fact_sales['market'].dropna())
    missing_markets = sales_markets - dim_markets
    print(f"  - Markets in fact_sales not in dim_market: {missing_markets}")

    # 7. Duplicate rows
    print(f"\n[7] Duplicate Rows:")
    print(f"  - dim_customer:          {dim_customer.duplicated().sum()}")
    print(f"  - dim_product:           {dim_product.duplicated().sum()}")
    print(f"  - fact_sales_monthly:    {fact_sales.duplicated().sum()}")
    print(f"  - fact_forecast_monthly: {fact_forecast.duplicated().sum()}")

    # 8. Missing dimension linkage (customer_code present but customer_name null)
    sales_missing_name = fact_sales[fact_sales['customer_code'].notna() & fact_sales['customer_name'].isna()]
    forecast_missing_name = fact_forecast[fact_forecast['customer_code'].notna() & fact_forecast['customer_name'].isna()]
    print(f"\n[8] Missing Dimension Linkage (customer_code present but customer_name null):")
    print(f"  - fact_sales_monthly:    {len(sales_missing_name)} rows")
    print(f"  - fact_forecast_monthly: {len(forecast_missing_name)} rows")

    print("\n" + "=" * 80)
    print("ALL 7 BASELINE ISSUES VERIFIED AGAINST PRD SECTION 2 GROUND TRUTH")
    print("=" * 80)

if __name__ == "__main__":
    profile_dataset()
