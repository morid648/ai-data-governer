# AI Data Governor — Interview Talking Points & 2-Minute Demo Narrative

## Executive Elevator Pitch (2 Minutes)

> "In data engineering and analytics, we spend countless hours building executive dashboards like Business Insights 360, but a dashboard is only as good as the integrity of the data beneath it. In real enterprise and fintech environments, incoming data is rarely clean—it's riddled with placeholder tokens like 'UNKNOWN', mixed string units in numeric metrics, trailing whitespace causing broken joins, and orphaned foreign keys.
>
> The traditional solution is painful and fragile: an analyst manually scans tables, writes ad-hoc SQL, and sends informal emails. It doesn't scale, and it leaves zero audit trail.
>
> To solve this, I designed and built **AI Data Governor**: an autonomous, multi-agent governance pipeline orchestrated in n8n over a PostgreSQL database. It employs three specialized AI agents with strict Draft-07 JSON Schema contracts:
> 1. A **Master Data Investigator Agent** powered by Groq and Kimi K2 that executes non-destructive schema inspection and deep scanning to detect and classify data anomalies into auto-fixable SQL candidates versus business policy questions.
> 2. A **Double-Approval Gate** ensuring zero unapproved writes touch the database—first confirming the data owner's availability, then presenting per-issue approval requests.
> 3. A **Data Issue Fixer Agent** powered by Gemini 2.5 Flash that generates and executes scoped PostgreSQL UPDATE and DELETE statements—with strict prohibitions against DDL.
> 4. A **Data Investigation Reporter Agent** that synthesizes the before-and-after audit lineage into an executive Google Doc report, configures public view permissions via Google Drive, and delivers it via Gmail.
>
> By separating scanning, fixing, and reporting into distinct agent boundaries and enforcing strict human approval, the system achieves 100% auditability without compromising governance or data safety."

---

## Technical Deep-Dive Talking Points

### 1. Why Three Agents Instead of a Single Mega-Agent?
- **Single-Agent Failure Mode**: Asking one LLM to detect, approve, generate SQL, execute queries, and format documents creates an oversized context window, increases hallucination risk, and makes schema enforcement almost impossible.
- **Architectural Separation of Concerns**:
  - **Investigator (Groq / Kimi K2)**: Optimized for fast, inexpensive token throughput across heavy read queries. Scoped to read-only tools.
  - **Fixer (Gemini 2.5 Flash)**: High-reasoning model receiving an isolated issue context. Restricted to DML statements (`UPDATE`, `DELETE`) with exact `WHERE` clauses.
  - **Reporter (Gemini 2.5 Flash)**: Specialized in document synthesis and styling standards (typography hierarchy, code block padding, executive summaries).

### 2. Why Mandatory Human-in-the-Loop Gating?
- **Fintech & Enterprise Reality**: In regulated industries (BFSI, healthcare, enterprise ERP), fully autonomous write access to production databases is a severe compliance violation.
- **Two-Tier Approval Architecture**:
  - *Tier 1 (Availability Gate)*: Asks the stakeholder if they have time for an audit review session before flooding their inbox with alerts.
  - *Tier 2 (Per-Issue Approval Gate)*: Displays exact description, sample values, and proposed remediation before any SQL executes.
- **Auditable Fallback**: Any rejected issue is seamlessly flagged as `status: "skipped"` with user rationale preserved in the final report.

### 3. Contract Enforcement via Draft-07 JSON Schema
- Rather than relying on fuzzy "please output valid JSON" prompt instructions, each agent is bound to an n8n **Structured Output Parser** using Draft-07 JSON Schema.
- Any malformed payload is intercepted immediately, preventing malformed SQL execution or corrupted reporting downstream.

### 4. Database Design Choice: Delayed Foreign Keys
- The target PostgreSQL schema intentionally omitted foreign keys during raw data ingestion.
- *Reasoning*: Enforcing strict foreign keys at load time causes ingestion pipelines to fail silently or reject records entirely, hiding systemic data upstream issues. Loading the raw data with text-tolerant fields (`sold_quantity text`) allows the governance agent to discover, quantify, and remediate the orphaned keys (`ZZZ####` pattern) in place.

### 5. Eliminating Onboarding Friction: Zero-SQL Drag-and-Drop Ingestion
- **The Problem Faced**: "Initially, onboarding a new dataset meant manually opening Supabase's SQL editor and running three separate scripts — create tables, seed raw records, verify baseline issues — before any audit could even start. That manual step undercut the whole point of a tool built around automation."
- **The Architectural Solution**: "I engineered a drag-and-drop ingestion path directly into the n8n workflow. An n8n Form Trigger accepts any CSV or Excel file, a custom Code node infers the schema on the fly (normalizing column names, detecting dates and numbers vs resilient text, and generating dynamic DDL), and Postgres nodes auto-create the table and batch-load the rows. The Master Data Investigator kicks off the moment the data lands — eliminating manual SQL and turning the system into a dataset-agnostic governance platform."

### 6. Real-World Multi-Agent Production Edge Cases & Debugging
- **Token Starvation vs Context Window (8K TPM vs 1M Window)**: "During live execution, an 8K Tokens-Per-Minute rate limit on a small model tier can silently cripple an agent when multi-table schemas are fed into tool loops. After two tool iterations, cumulative prompt tokens triggered 429 backoffs, consuming the iteration budget and causing premature halts (`Agent stopped due to max iterations`). Migrating the Investigator to Google Gemini (1M token window) and calibrating `maxIterations` to 15 completely resolved the bottleneck."
- **Sub-Workflow Tool Decoupling (`toolWorkflow`)**: "In n8n, AI agents execute database modifications through dedicated sub-workflows rather than monolithic tool nodes. When a sub-workflow reference is unlinked, the agent encounters runtime routing errors. Implementing a modular `SQL Query executor` sub-workflow with an `executeWorkflowTrigger` cleanly encapsulated database permissions and allowed robust query routing."

---

## Production Roadmap (What I Would Enhance at Enterprise Scale)
1. **Orchestrator**: Transition from n8n to Apache Airflow / Cloud Composer for scheduled SLA monitoring and distributed worker scaling.
2. **Approval Channels**: Integrate Slack / Microsoft Teams interactive cards alongside Gmail for real-time operations.
3. **Database Audit Table**: Write all fix executions and rollback snapshots into a dedicated `audit_governance_log` PostgreSQL table for immutable compliance logs.
