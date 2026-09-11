#!/usr/bin/env python3
"""
Synthetic Sample Dataset Generator for AI Data Governor (TASK-9.2)
Generates a sanitized, lightweight public dataset in data/synthetic_raw/
with the identical 7 data-quality anomalies seeded systematically.
"""

import os
import random
import pandas as pd

random.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "synthetic_raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_synthetic_data():
    print("Generating synthetic datasets with intentional data anomalies...")

    # 1. dim_market (~15 markets)
    markets_data = [
        {"market": "India", "sub_zone": "South Asia", "region": "APAC"},
        {"market": "USA", "sub_zone": "North America", "region": "NA"},
        {"market": "Germany", "sub_zone": "EU", "region": "EMEA"},
        {"market": "UK", "sub_zone": "EU", "region": "EMEA"},
        {"market": "France", "sub_zone": "EU", "region": "EMEA"},
        {"market": "Japan", "sub_zone": "East Asia", "region": "APAC"},
        {"market": "Australia", "sub_zone": "ANZ", "region": "APAC"},
        {"market": "Brazil", "sub_zone": "LATAM", "region": "LATAM"},
        # Intentionally seeded missing sub_zone / region
        {"market": "Norway", "sub_zone": None, "region": "EMEA"},
        {"market": "Sweden", "sub_zone": "Nordics", "region": None},
        {"market": "Singapore", "sub_zone": "SE Asia", "region": "APAC"},
        {"market": "UAE", "sub_zone": "Middle East", "region": "EMEA"},
    ]
    dim_market = pd.DataFrame(markets_data)

    # 2. dim_customer (~40 customers)
    customers = [
        "Amazon", "Amazon ", "Atliq Exclusive", "AltiQ Exclusive", "Flipkart", "Best Buy",
        "Walmart", "Target", "Costco", "Croma", "Reliance Digital", "Currys", "MediaMarkt",
        "Boulanger", "Euronics", "Staples", "Office Depot", "Argos", "John Lewis", "Fnac"
    ]
    cust_rows = []
    for i in range(1, 41):
        code = f"9000{i:04d}"
        cust_name = customers[(i - 1) % len(customers)]
        market = markets_data[(i - 1) % len(markets_data)]["market"]
        platform = "E-Commerce" if i % 2 == 0 else "Brick & Mortar"
        channel = "Retailer" if i % 3 == 0 else "Direct"
        
        # Seed anomalies
        if i == 5:
            platform = "UNKNOWN"
        elif i == 12:
            platform = None
        elif i == 18:
            cust_name = None
            
        cust_rows.append({
            "customer": cust_name,
            "market": market,
            "platform": platform,
            "channel": channel,
            "customer_code": code
        })
    
    # Add duplicates
    cust_rows.append(cust_rows[0].copy())
    cust_rows.append(cust_rows[2].copy())
    dim_customer = pd.DataFrame(cust_rows)

    # 3. dim_product (~30 products)
    products = [
        ("P101", "Peripherals", "Internal", "Storage", "AQ NVMe SSD", "1TB"),
        ("P102", "Peripherals", "Internal", "Storage", "AQ SATA SSD", "500GB"),
        ("P103", "Peripherals", "Internal", "Memory", "AQ DDR4 RAM", "16GB"),
        ("P104", "Peripherals", "Internal", "Memory", "AQ DDR5 RAM", "32GB"),
        ("P105", "Peripherals", "Audio", "Headphones", "AQ Bass Master", "Wireless"),
        ("P106", "Peripherals", "Audio", "Headphones", "AQ Studio Pro", "Wired"),
        ("P107", "Peripherals", "Accessories", "Mouse", "AQ Gaming Mouse", "RGB"),
        ("P108", "Peripherals", "Accessories", "Keyboard", "AQ Mech Keyboard", "Blue Switch"),
        ("P109", "PC", "Desktop", "Custom PC", "AQ Titan Gaming", "RTX4080"),
        ("P110", "PC", "Notebook", "Ultrabook", "AQ SlimBook 14", "i7 16GB"),
        # Anomalies
        ("P111", "Peripherals", "Internal", "UNKNOWN", "AQ Generic Fan", "120mm"),
        ("P112", "Peripherals", "Internal", "-", "AQ RGB Strip", "1m"),
        ("P113", "Peripherals", "Accessories", None, "AQ Mousepad", "XL"),
        ("P114", "Peripherals", "Accessories", "Mouse", "AQ Wireless Mouse", None),
    ]
    prod_rows = []
    for p in products:
        prod_rows.append({
            "product_code": p[0],
            "division": p[1],
            "segment": p[2],
            "category": p[3],
            "product": p[4],
            "variant": p[5]
        })
    # Add duplicate
    prod_rows.append(prod_rows[0].copy())
    dim_product = pd.DataFrame(prod_rows)

    # 4. fact_sales_monthly & fact_forecast_monthly (~500 rows each)
    sales_rows = []
    forecast_rows = []
    dates = ["2024-01-01", "2024-02-01", "2024-03-01", "2024-04-01", "2024-05-01", "2024-06-01"]

    for i in range(500):
        dt = random.choice(dates)
        p = random.choice(prod_rows)
        c = random.choice(cust_rows)
        
        # 10% orphan customer code (ZZZ#### pattern)
        if i % 10 == 0:
            cust_code = f"ZZZ{random.randint(1000, 9999)}"
            cust_name = None # Missing dimension linkage
        else:
            cust_code = c["customer_code"]
            cust_name = c["customer"]

        # Missing market anomaly (Canada not in dim_market)
        if i % 25 == 0:
            market = "Canada"
        else:
            market = c["market"]

        qty_num = random.randint(5, 500)
        # 10% non-numeric "X units" string suffix
        if i % 10 == 3:
            sold_qty = f"{qty_num} units"
            forecast_qty = f"{qty_num + random.randint(-10, 10)} units"
        else:
            sold_qty = str(qty_num)
            forecast_qty = str(qty_num + random.randint(-10, 10))

        row_sales = {
            "date": dt,
            "division": p["division"],
            "category": p["category"],
            "product_code": p["product_code"],
            "product": p["product"],
            "market": market,
            "platform": c["platform"],
            "channel": c["channel"],
            "customer_code": cust_code,
            "customer_name": cust_name,
            "sold_quantity": sold_qty
        }
        
        row_forecast = {
            "date": dt,
            "division": p["division"],
            "category": p["category"],
            "product_code": p["product_code"],
            "product": p["product"],
            "market": market,
            "platform": c["platform"],
            "channel": c["channel"],
            "customer_code": cust_code,
            "customer_name": cust_name,
            "forecast_quantity": forecast_qty
        }
        
        sales_rows.append(row_sales)
        forecast_rows.append(row_forecast)

    # Add duplicate rows
    for _ in range(15):
        sales_rows.append(sales_rows[random.randint(0, 50)].copy())
        forecast_rows.append(forecast_rows[random.randint(0, 50)].copy())

    fact_sales = pd.DataFrame(sales_rows)
    fact_forecast = pd.DataFrame(forecast_rows)

    # Save to CSV
    dim_customer.to_csv(os.path.join(OUTPUT_DIR, "dim_customer.csv"), index=False)
    dim_market.to_csv(os.path.join(OUTPUT_DIR, "dim_market.csv"), index=False)
    dim_product.to_csv(os.path.join(OUTPUT_DIR, "dim_product.csv"), index=False)
    fact_sales.to_csv(os.path.join(OUTPUT_DIR, "fact_sales_monthly.csv"), index=False)
    fact_forecast.to_csv(os.path.join(OUTPUT_DIR, "fact_forecast_monthly.csv"), index=False)

    print("Synthetic dataset successfully created:")
    print(f"  - dim_customer:          {len(dim_customer)} rows")
    print(f"  - dim_market:            {len(dim_market)} rows")
    print(f"  - dim_product:           {len(dim_product)} rows")
    print(f"  - fact_sales_monthly:    {len(fact_sales)} rows")
    print(f"  - fact_forecast_monthly: {len(fact_forecast)} rows")

if __name__ == "__main__":
    generate_synthetic_data()
