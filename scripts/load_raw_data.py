#!/usr/bin/env python3
"""
Raw Data Loader for AI Data Governor (TASK-1.2)
Loads the 5 raw dirty CSV datasets into PostgreSQL (Supabase).
Supports:
1. Direct connection via psycopg2/SQLAlchemy using .env credentials
2. Generating a portable SQL dump (scripts/01b_insert_raw_data.sql) for execution
   in Supabase SQL Editor or psql CLI.
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

TABLE_FILES = [
    ("dim_customer", "dim_customer.csv"),
    ("dim_market", "dim_market.csv"),
    ("dim_product", "dim_product.csv"),
    ("fact_sales_monthly", "fact_sales_monthly.csv"),
    ("fact_forecast_monthly", "fact_forecast_monthly.csv")
]

def get_db_url():
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    
    host = os.getenv("POSTGRES_HOST")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD")
    db = os.getenv("POSTGRES_DB", "postgres")
    port = os.getenv("POSTGRES_PORT", "5432")
    
    if host and password:
        return f"postgresql://{user}:{password}@{host}:{port}/{db}?sslmode=require"
    return None

def generate_sql_insert_dump():
    """Generates an SQL script with INSERT statements for all 5 dirty tables."""
    out_file = os.path.join(SCRIPTS_DIR, "01b_insert_raw_data.sql")
    print(f"Generating portable SQL insert dump at: {out_file} ...")
    
    with open(out_file, "w", encoding="utf-8") as out:
        out.write("-- AI Data Governor: Raw Dirty Data Ingestion Dump\n")
        out.write("-- Run 01_create_tables.sql before running this file.\n\n")
        
        for table_name, csv_filename in TABLE_FILES:
            csv_path = os.path.join(DATA_DIR, csv_filename)
            if not os.path.exists(csv_path):
                print(f"Warning: {csv_path} not found.")
                continue
            
            df = pd.read_csv(csv_path, dtype=str)
            print(f"  Processing {table_name} ({len(df)} rows)...")
            
            columns = list(df.columns)
            col_str = ", ".join([f'"{c}"' for c in columns])
            
            # Write in batches of 500 rows
            batch_size = 500
            for start_idx in range(0, len(df), batch_size):
                batch = df.iloc[start_idx:start_idx + batch_size]
                value_rows = []
                for _, row in batch.iterrows():
                    escaped_vals = []
                    for val in row:
                        if pd.isna(val):
                            escaped_vals.append("NULL")
                        else:
                            clean_val = str(val).replace("'", "''")
                            escaped_vals.append(f"'{clean_val}'")
                    value_rows.append(f"({', '.join(escaped_vals)})")
                
                out.write(f"INSERT INTO {table_name} ({col_str}) VALUES\n")
                out.write(",\n".join(value_rows))
                out.write(";\n\n")
                
    print(f"Successfully generated SQL insert dump: {out_file}")

def direct_db_load(db_url):
    """Loads CSV data directly into the database using psycopg2 / SQLAlchemy."""
    print("Connecting to PostgreSQL database...")
    from sqlalchemy import create_engine
    
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        print("Connected successfully. Verifying tables...")
        for table_name, csv_filename in TABLE_FILES:
            csv_path = os.path.join(DATA_DIR, csv_filename)
            if not os.path.exists(csv_path):
                print(f"Warning: {csv_path} not found.")
                continue
            
            df = pd.read_csv(csv_path, dtype=str)
            print(f"Loading {len(df)} rows into '{table_name}'...")
            
            # Clear existing dirty data if any
            conn.execute(f"TRUNCATE TABLE {table_name};")
            
            # Load in chunks
            df.to_sql(table_name, engine, if_exists="append", index=False, chunksize=1000)
            print(f"Loaded {table_name} successfully.")
    
    print("\nAll 5 tables loaded successfully into target database!")

def main():
    db_url = get_db_url()
    if db_url and "your_supabase" not in db_url and "xxxxxxxx" not in db_url:
        try:
            print("Found database credentials. Attempting direct DB ingestion...")
            direct_db_load(db_url)
            return
        except Exception as e:
            print(f"Direct DB connection failed: {e}")
            print("Falling back to generating SQL insert dump...")
    
    print("Generating portable SQL insert dump for Supabase / PostgreSQL...")
    generate_sql_insert_dump()
    print("\nTo load data into Supabase:")
    print("1. Open Supabase SQL Editor for your project.")
    print("2. Run 'scripts/01_create_tables.sql' to create the 5 tables.")
    print("3. Run 'scripts/01b_insert_raw_data.sql' (or configure .env and re-run this script).")

if __name__ == "__main__":
    main()
