# LinkedIn Project Announcement Draft (TASK-9.6)

**Headline: Why 80% of Data Cleaning Should Be Autonomous (And Why the Other 20% Needs Human-in-the-Loop)**

Before an executive dashboard or machine learning model can deliver value, data engineers and analysts spend hours on an unglamorous chore: auditing dirty datasets, hunting down rogue placeholder tokens like "UNKNOWN", stripping string suffixes from numeric fields, and writing ad-hoc SQL fixes.

Worse, in regulated enterprise and fintech environments, fully autonomous database writes are a major compliance risk.

To tackle this, I built **AI Data Governor** — an autonomous, multi-agent data-quality audit and remediation pipeline orchestrated in n8n over a PostgreSQL database.

Here’s how the multi-agent architecture works:

1️⃣ **Master Data Investigator Agent (Groq / Kimi K2)**: Performs non-destructive scans across all tables and schemas, surfacing data quality anomalies (missing values, trailing whitespace, unit suffixes, orphaned keys) and classifying them into "Fixable with SQL" vs. "Needs Policy Establishment."

2️⃣ **Two-Tier Human Approval Gate**: Zero unapproved writes touch the database. The system first checks stakeholder availability via an interactive email gate, then delivers per-issue approvals showing the issue context and proposed SQL remediation.

3️⃣ **Data Issue Fixer Agent (Google Gemini 2.5 Flash)**: Executes approved PostgreSQL UPDATE/DELETE statements under strict guardrails (zero DDL allowed).

4️⃣ **Data Investigation Reporter Agent (Google Gemini 2.5 Flash)**: Synthesizes the full lineage into a structured Google Doc health report, provisions public view access via Google Drive, and delivers the link via Gmail.

⚡ **Key Technical Highlights**:
- Zero-SQL drag-and-drop onboarding: Upload any CSV or Excel file via an n8n Form Trigger; a custom Code node dynamically infers column types, generates PostgreSQL DDL, batch-loads rows, and kicks off the audit instantly.
- Contract-driven multi-agent architecture: Draft-07 JSON Schema validation via n8n Structured Output Parsers on every agent boundary.
- Full auditability: Every executed SQL statement, skipped item, and policy issue is preserved in the final report.
- Synthetic benchmark dataset & reproducible SQL scripts included.

🔗 **GitHub Repository & Architecture**: https://github.com/your-username/ai-data-governor

Would love to hear how your teams handle data hygiene and governance before data lands in reporting layers!

#DataEngineering #DataGovernance #AIAgents #PostgreSQL #n8n #DataQuality #Fintech #Gemini #Groq
