#!/usr/bin/env python3
"""
Token Optimization Script for AI Data Governor (Groq Free Tier)
Reduces context window & token usage to operate reliably under Groq's 8k limits.
"""

import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

COMPACT_PROMPT = """You are Master Data Health Checker for PostgreSQL.
Scan the database schema and run targeted diagnostic queries to detect data quality anomalies:
1. NULLs or empty strings in key columns
2. Placeholder tokens like 'UNKNOWN' or '-'
3. Inconsistent whitespace / trailing spaces
4. Non-numeric unit suffixes (e.g. ' units' in sold_quantity / forecast_quantity)
5. Orphan foreign keys (e.g. customer_code not in dim_customer or starting with 'ZZZ')
6. Unregistered dimension values (e.g. market not in dim_market)
7. Duplicate rows

Strategy:
- Use Postgres_Schmea once to inspect table structures.
- Use Query Tool1 to run focused diagnostic queries across tables using COUNT, WHERE conditions, and LIMIT 5.
- Complete your inspection in 4 to 6 queries, then immediately synthesize your final response.

Output Contract (Strict JSON array only):
[
  {
    "issue_id": "ISSUE-001",
    "category": "Fixable with SQL",
    "description": "Concise summary under 200 chars",
    "sample_values": ["sample1", "sample2"],
    "suggestion": "Proposed remediation under 200 chars"
  }
]
Categories must be either "Fixable with SQL" or "Needs Policy Establishment".
If no issues found, return []. JSON array only, no markdown."""

COMPACT_SCHEMA_QUERY = """SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name NOT LIKE 'pg_%'
ORDER BY table_name, ordinal_position
LIMIT 60;"""

paths = [
    os.path.join(BASE_DIR, "workflow", "ai_data_governor_workflow.json"),
    os.path.join(BASE_DIR, "workflow", "data_governor_n8n_workflow.json")
]

for path in paths:
    if not os.path.exists(path):
        continue
    with open(path, "r", encoding="utf-8") as f:
        wf = json.load(f)

    for node in wf.get("nodes", []):
        # 1. Groq Model -> llama-3.1-8b-instant (30k TPM rate limit vs 6k TPM for 70b)
        if "groq" in node.get("type", "").lower():
            node.setdefault("parameters", {})
            node["parameters"]["model"] = "llama-3.1-8b-instant"
            node["parameters"]["options"] = {
                "maxTokens": 1500,
                "temperature": 0.1
            }
            print(f"[{os.path.basename(path)}] Switched Groq model to llama-3.1-8b-instant (maxTokens=1500)")

        # 2. Cap Agent maxIterations to 15 (gives enough room for full audit without infinite loops)
        if "Investigator" in node.get("name", ""):
            params = node.setdefault("parameters", {})
            options = params.setdefault("options", {})
            options["systemMessage"] = COMPACT_PROMPT
            options["maxIterations"] = 15
            print(f"[{os.path.basename(path)}] Set Investigator iterations to 15 and refined strategy prompt")

        # 3. Scope Schema Query to reduce returned payload
        if "Schmea" in node.get("name", "") or "Schema" in node.get("name", ""):
            if "parameters" in node and "query" in node["parameters"]:
                node["parameters"]["query"] = COMPACT_SCHEMA_QUERY
                print(f"[{os.path.basename(path)}] Scoped schema query on {node['name']}")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(wf, f, indent=2)

print("\nAll Groq token optimizations successfully applied!")
