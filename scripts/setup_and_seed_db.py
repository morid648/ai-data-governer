#!/usr/bin/env python3
"""
Seed Dirty Baseline Data into Supabase Database for AI Data Governor
Creates all 5 tables from 01_create_tables.sql and populates them from CSVs in data/raw/.
"""

import os
import sys
import json
import psycopg2
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
DDL_FILE = os.path.join(BASE_DIR, "scripts", "01_create_tables.sql")
CREDS_FILE = os.path.join(BASE_DIR, "scratch", "credentials_backup.json")

def main():
    print("=" * 80)
    print("AI DATA GOVERNOR -- INITIALIZING & SEEDING SUPABASE DATABASE")
    print("=" * 80)

    with open(CREDS_FILE, "r", encoding="utf-8") as f:
        creds = json.load(f)

    pg_cred = next(c for c in creds if c["id"] == "MmILiTHNtAMs1LRT")["data"]
    host = pg_cred["host"]
    password = pg_cred["password"]

    print(f"Connecting to database at {host}...")
    conn = psycopg2.connect(
        host=host,
        port=5432,
        dbname="postgres",
        user="postgres",
        password=password,
        sslmode="require",
        connect_timeout=15
    )
    conn.autocommit = True
    cur = conn.cursor()

    # 1. Execute DDL
    print(f"\n[1] Applying Schema DDL from {os.path.basename(DDL_FILE)}...")
    with open(DDL_FILE, "r", encoding="utf-8") as f:
        ddl_sql = f.read()
    cur.execute(ddl_sql)
    print("  Tables created successfully: dim_customer, dim_market, dim_product, fact_sales_monthly, fact_forecast_monthly")

    # 2. Ingest CSVs
    tables = [
        ("dim_customer", "dim_customer.csv"),
        ("dim_market", "dim_market.csv"),
        ("dim_product", "dim_product.csv"),
        ("fact_sales_monthly", "fact_sales_monthly.csv"),
        ("fact_forecast_monthly", "fact_forecast_monthly.csv")
    ]

    print("\n[2] Seeding Raw Dirty CSV Data...")
    for table_name, csv_filename in tables:
        csv_path = os.path.join(DATA_DIR, csv_filename)
        if not os.path.exists(csv_path):
            print(f"  Warning: {csv_path} does not exist!")
            continue

        df = pd.read_csv(csv_path, dtype=str)
        cols = list(df.columns)
        col_names = ", ".join([f'"{c}"' for c in cols])
        placeholders = ", ".join(["%s"] * len(cols))
        insert_sql = f'INSERT INTO "{table_name}" ({col_names}) VALUES ({placeholders})'

        # Convert NaN to None for psycopg2
        data_tuples = [tuple(None if pd.isna(x) else str(x) for x in row) for row in df.itertuples(index=False)]

        print(f"  Seeding {table_name}: {len(data_tuples)} records...", end=" ", flush=True)
        psycopg2.extras = __import__("psycopg2.extras").extras
        psycopg2.extras.execute_batch(cur, insert_sql, data_tuples, page_size=2000)
        print("DONE.")

    # 3. Verify Counts
    print("\n[3] Verifying Database Row Counts:")
    for table_name, _ in tables:
        cur.execute(f'SELECT count(*) FROM "{table_name}";')
        cnt = cur.fetchone()[0]
        print(f"  - {table_name:<24}: {cnt:>6} rows")

    cur.close()
    conn.close()
    print("\n" + "=" * 80)
    print("DATABASE SEEDING COMPLETE -- ALL TABLES POPULATED WITH DIRTY TEST DATA")
    print("=" * 80)

if __name__ == "__main__":
    main()
