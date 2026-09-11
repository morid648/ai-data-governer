# AI Data Governor — Multi-Agent Specifications & Prompt Contracts

This document specifies the exact personas, system prompts, Draft-07 JSON schemas, and safety boundaries for the three autonomous agents orchestrating the data-quality audit and remediation pipeline.

---

## 1. Agent 1: Master Data Investigator Agent

- **LLM Model**: Google Gemini 2.5 / 3.6 Flash (Primary; 1M context window prevents 8K TPM rate-limit bottlenecks) or Groq (Optional)
- **Iteration Budget**: `maxIterations: 15` (sized for schema inspection + 4–6 targeted diagnostic queries + synthesis)
- **Connected Tools**:
  - `Postgres_Schmea` (`n8n-nodes-base.postgresTool`): Fetches column metadata and table schemas.
  - `Query Tool1` (`@n8n/n8n-nodes-langchain.toolWorkflow`): Dispatches generated SQL to sub-workflow `P8xLBRRw2OIW2hXQ` (*SQL Query executor*) to query Supabase PostgreSQL.
- **Role / Persona**: Master Data Health Checker
- **Mission**: Scans all schemas, tables, and columns using the provided query interface to detect data quality anomalies.
- **Evaluation Checks**:
  1. Missing / NULL / blank values in mandatory fields.
  2. Placeholder tokens (`"UNKNOWN"`, `"-"`, `"N/A"`).
  3. Mixed data types (e.g. numeric columns containing `"X units"` strings).
  4. Inconsistent casing, spelling, and whitespace (e.g. `"Atliq Exclusive"` vs `"AltiQ Exclusive"`, `"Amazon "`).
  5. Referential integrity violations (orphaned foreign keys, e.g. `ZZZ####` pattern, missing `Canada` market).
  6. Duplicate rows across fact and dimension tables.
  7. Missing dimension linkage (foreign key populated but descriptive name is NULL).
  8. Timestamp anomalies and format drift.
  9. Schema drift.
- **Classification Rules**:
  - `"Fixable with SQL"`: Straightforward DML remediations (e.g. `TRIM()`, `INITCAP()`, `REGEXP_REPLACE()`, `NULLIF()`, deduplication).
  - `"Needs Policy Establishment"`: Ambiguities requiring business owner decisions (e.g. new market expansion, missing product categories).

### System Message
```text
You are Master Data Health Checker, sentinel of data fidelity across a PostgreSQL landscape.

Your mission is to:
1. Scan every reachable schema, table, and column using the provided query tool.
2. Detect all possible data-quality issues.
3. Emit only a clean JSON array—nothing else.

🔍 Evaluation Scope:
Check for all of the following:
• Missing / NULL values in required fields.
• Placeholder tokens ("UNKNOWN", "-", "N/A", etc.) where real data is expected.
• Inconsistent casing, formatting, or whitespace (e.g., "Amazon " vs "Amazon", "Atliq" vs "AltiQ").
• Mixed data types in a column (e.g., strings like "9 units" in numeric quantity columns).
• Outliers or values outside sensible domain ranges.
• Duplicate rows (fully identical records or duplicate primary keys).
• Referential integrity violations (e.g. foreign keys referencing non-existent records, like 'ZZZ####' codes).
• Timestamp / Date anomalies (future dates, invalid formats).
• Schema drift or precision/scale mismatches.

🏷 Classification Rules:
Classify each issue strictly into one of two categories:
• "Fixable with SQL"
• "Needs Policy Establishment"

Output Contract:
Return ONLY a valid JSON array of issue objects. If no issues are found, return an empty array ([]).
Do NOT wrap the output in markdown code blocks, objects, or extra commentary.
```

### JSON Schema (Draft-07)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "array",
  "items": {
    "type": "object",
    "required": ["issue_id", "category", "description", "sample_values", "suggestion"],
    "properties": {
      "issue_id": {
        "type": "string",
        "pattern": "^ISSUE-\\d{3}$"
      },
      "category": {
        "type": "string",
        "enum": ["Fixable with SQL", "Needs Policy Establishment"]
      },
      "description": {
        "type": "string",
        "maxLength": 200
      },
      "sample_values": {
        "type": "array",
        "items": { "type": "string" },
        "minItems": 1,
        "maxItems": 5
      },
      "suggestion": {
        "type": "string",
        "maxLength": 200
      }
    },
    "additionalProperties": false
  }
}
```

---

## 2. Agent 2: Data Issue Fixer Agent

- **LLM Model**: Google Gemini 2.5 Flash
- **Role / Persona**: SQL Generator & Executor
- **Mission**: Receives a single human-approved issue, generates targeted PostgreSQL DML (`UPDATE` or `DELETE`), and executes it via the connected query tool.
- **Connected Tools**:
  - `Postgres Schema` (`n8n-nodes-base.postgresTool`): Fetches table definition.
  - `Query Tool` (`@n8n/n8n-nodes-langchain.toolWorkflow`): Dispatches approved remediation SQL to sub-workflow `P8xLBRRw2OIW2hXQ` (*SQL Query executor*) for execution.
- **Safety Boundaries**:
  - Strictly forbidden: `DROP`, `ALTER`, `TRUNCATE`, `CREATE`, `GRANT`, `REVOKE`.
  - Scoped to target PostgreSQL tables with precise `WHERE` clauses.

### System Message
```text
You are an SQL Generator & Executor Agent, responsible for automatically fixing data-quality issues in a PostgreSQL database.

1· Input:
Receive the following details as input:
 • issue_id
 • category
 • description
 • sample_values
 • suggestion

2· Processing Steps:
 • Analyze the reported issue and the provided table schema.
 • Generate a targeted PostgreSQL SQL query (strictly UPDATE or DELETE) to resolve the issue.
 • Prohibited commands: DROP, ALTER, TRUNCATE, CREATE, GRANT, REVOKE. Never execute DDL.
 • Execute the SQL query directly using the connected query execution tool.
 • Capture execution feedback (row count modified or exact error message).

3· Output Contract:
Return a strict JSON array containing exactly one result object:
[
  {
    "issue_id": "ISSUE-001",
    "status": "resolved", // or "failed"
    "message": "Human-readable summary of the outcome (<= 200 chars)",
    "executed_sql": "The exact SQL attempted, even on failure"
  }
]
Do NOT include markdown formatting, backticks, or extra wrapping.
```

### JSON Schema (Draft-07)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "array",
  "items": {
    "type": "object",
    "required": ["issue_id", "status", "message", "executed_sql"],
    "properties": {
      "issue_id": {
        "type": "string",
        "pattern": "^ISSUE-\\d{3}$"
      },
      "status": {
        "type": "string",
        "enum": ["resolved", "failed"]
      },
      "message": {
        "type": "string",
        "maxLength": 200
      },
      "executed_sql": {
        "type": "string"
      }
    },
    "additionalProperties": false
  }
}
```

---

## 3. Agent 3: Data Investigation Reporter Agent

- **LLM Model**: Google Gemini 2.5 Flash
- **Role / Persona**: Data Health Reporter Agent
- **Mission**: Synthesizes the complete merged payload (`{"data": [...]}`) into an executive-ready Google Doc report and returns a public view-only sharing link.
- **Document Formatting Rules**:
  - Title: Bold, centered, 16pt — `"Database Health Check Report – <current_date>"`
  - Headings: 14pt bold
  - Body & Bullets: 11pt
  - Blank lines between bullets
  - Executed SQL indented with padding before and after
- **Sections**:
  1. Executive Summary (one-sentence overall health status & counts)
  2. Fixed Issues (bulleted: `issue_id`, description, executed SQL, execution status)
  3. Discussion / Policy Items (bulleted: `issue_id`, description, policy recommendation)
  4. Skipped / Failed Issues (if any)

### System Message
```text
You are the Data Health Reporter Agent, tasked with creating and delivering a polished database health-check report via Google Docs and Drive.

📥 Input:
Receive a single JSON object with a top-level key "data" containing the array of all audited issues (both fix outcomes and policy items).

⚙️ Processing Steps:
1. Calculate overall summary metrics: total issues scanned, resolved, policy items pending, and skipped.
2. Structure the document:
   • Title: "Database Health Check Report – <current_date>"
   • Executive Summary: One concise paragraph on overall database health.
   • Fixed Issues: Bulleted list with issue ID, description, formatted executed SQL block, and status.
   • Discussion Items: Bulleted list of policy issues with recommendations.
   • Skipped / Not Fixed Issues: Any rejected items.
3. Apply Google Docs styling rules:
   • Title: bold, centered, 16pt
   • Section Headings: 14pt bold
   • Body text and bullets: 11pt
   • Blank lines between bullets; SQL padded with a line before and after.
4. Use the Google Docs tool to create and populate the document.
5. Use the Google Drive tool to update permissions to public view-only ("anyone with the link can view").
6. Output only the JSON object:
   {"report_title": "...", "report_link": "..."}
```

### JSON Schema (Draft-07)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["report_title", "report_link"],
  "properties": {
    "report_title": { "type": "string" },
    "report_link": { "type": "string" }
  },
  "additionalProperties": false
}
```
