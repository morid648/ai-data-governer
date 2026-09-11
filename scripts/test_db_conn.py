import psycopg2
import json

with open("scratch/credentials_backup.json", "r") as f:
    creds = json.load(f)

pg_cred = next(c for c in creds if c["id"] == "MmILiTHNtAMs1LRT")["data"]
host = pg_cred["host"]
password = pg_cred["password"]

print(f"Connecting to {host}...")
try:
    conn = psycopg2.connect(
        host=host,
        port=5432,
        dbname="postgres",
        user="postgres",
        password=password,
        sslmode="require",
        connect_timeout=10
    )
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;")
    tables = cur.fetchall()
    print(f"Connected successfully! Found {len(tables)} tables:")
    for t in tables:
        tname = t[0]
        cur.execute(f'SELECT count(*) FROM "{tname}";')
        cnt = cur.fetchone()[0]
        print(f"  - {tname}: {cnt} rows")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
