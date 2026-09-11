# PRD: AI Data Governor — Autonomous Data-Quality Audit & Remediation Agent

| | |
|---|---|
| **Owner** | Anshul |
| **Status** | Draft — ready to build |
| **Type** | Portfolio project (AI automation × data engineering × governance) |
| **Source material** | codebasics "AI Automation for Data Professionals" — Data Governor project resources |
| **Last updated** | 11 Sep 2026 |

---

## 1. One-liner

An n8n-orchestrated, multi-agent AI system that audits the AtliQ Hardwares sales/forecast database for data-quality issues, gets human approval, auto-fixes what it safely can with generated SQL, and delivers a formatted Google Doc health report by email — turning a manual, table-by-table cleanup chore into a one-click, auditable workflow.

## 2. Background & Problem Statement

The resource pack ships a real "dirty" version of the AtliQ Hardwares dataset (the same business used in the Business Insights 360 Power BI project) across five CSVs: `dim_customer`, `dim_market`, `dim_product`, `fact_sales_monthly`, `fact_forecast_monthly`. Profiling the actual files surfaces concrete, non-generic problems this project needs to solve — not hypothetical ones:

**Confirmed data-quality issues in the raw data**

| Issue type | Where | Evidence |
|---|---|---|
| Missing values | `dim_customer.customer` (10 blank), `dim_customer.platform` (8 blank), `dim_market.sub_zone`/`region` (3/2 blank), `dim_product.category` (10 blank), `dim_product.variant` (20 blank) | Null counts from profiling |
| Placeholder tokens (multiple representations of "unknown") | `dim_customer.platform` has 3 rows literally `"UNKNOWN"`; `dim_product.category` has 6 rows `"UNKNOWN"` **and** 5 rows `"-"` **and** 10 nulls — three different encodings of the same missing-data concept | value_counts on both columns |
| Mixed data types in a numeric column | `fact_sales_monthly.sold_quantity`: 2,150 of 21,503 rows are strings like `"9 units"` instead of a bare number; `fact_forecast_monthly.forecast_quantity`: 2,180 of 21,802 rows have the same `"X units"` suffix | regex match against numeric pattern |
| Inconsistent naming / casing / spelling for the same entity | `dim_customer.customer`: `"Atliq Exclusive"` vs `"AltiQ Exclusive"`; trailing whitespace on `"Amazon "` vs `"Amazon"` | manual scan of unique values |
| Referential integrity violations | 1,036 distinct `customer_code` values in `fact_sales_monthly` don't exist in `dim_customer` — almost all following a suspicious `ZZZ####` pattern (1,075 rows total) instead of the real 8-digit codes used elsewhere, i.e. a placeholder code, not a real one; `market = "Canada"` appears in `fact_sales_monthly` but not in `dim_market` | anti-join on keys |
| Duplicate rows | 610 duplicate rows in `fact_sales_monthly`, 514 in `fact_forecast_monthly`, 9 in `dim_customer`, 16 in `dim_product` | `.duplicated().sum()` |
| Missing dimension linkage | 1,073 rows in `fact_sales_monthly` and 1,080 in `fact_forecast_monthly` have a `customer_code` but a null `customer_name` — concentrated in the `ZZZ####`-coded rows | cross-tab of null names vs code pattern |

This is the same *class* of problem every BFSI/fintech data team deals with before any dashboard, model, or regulatory report can be trusted — which is exactly why it's a strong portfolio piece: it demonstrates data governance instincts on top of the finance-domain credibility from the CMA and the ITC valuation/Business Insights 360 projects, not just another dashboard.

**The manual alternative** the project replaces: an analyst opening five CSVs (or tables), eyeballing each column for placeholders/nulls/format drift, writing ad-hoc SQL fixes, and emailing a summary — repeated every time new data lands. That doesn't scale and isn't auditable.

## 3. Goals

1. Stand up a working, end-to-end n8n workflow that audits a live Postgres (Supabase) copy of the AtliQ dataset and classifies every issue it finds as **"Fixable with SQL"** or **"Needs Policy Establishment."**
2. Gate every auto-fix behind explicit human approval (no silent writes to the database).
3. Produce a shareable, formatted report (Google Doc) summarizing what was found, fixed, and left for discussion, delivered by email.
4. Package the whole thing as a public GitHub repo with a synthetic/sanitized dataset, README, architecture diagram, and a sample report — reusing the pattern already established with the CarePlus pipeline project.
5. Be able to talk through the design (agent boundaries, approval gating, prompt/schema contracts) confidently in an interview, not just say "I did a course project."

## 4. Success Metrics

- Workflow runs end-to-end on the AtliQ dataset without manual intervention beyond the two approval clicks (stakeholder go-ahead + per-issue or batch approval).
- The audit agent's classification is checked against the manually-profiled issue list above — target ≥90% of the known issue types actually surfaced.
- 100% of "Fixable with SQL" issues are only executed after an explicit approval; zero unapproved writes in testing.
- Final report Google Doc renders with correct structure (title, executive summary, fixed issues with executed SQL, discussion items) and is shared with "anyone with the link can view."
- Repo is public, has a README a recruiter can skim in under 2 minutes, and includes a real (or clearly-labeled sample) report link/screenshot.

## 5. Non-Goals

- Not building a general-purpose data-quality platform — scoped to this one dataset and this one workflow.
- Not implementing fully autonomous fixes with no human in the loop — the approval gate is a deliberate, permanent design choice, not a placeholder to remove later.
- Not covering "Needs Policy Establishment" issues end-to-end (e.g., deciding *what* the policy should be) — the system only surfaces and documents them.
- Not a production system with multi-tenant auth, RBAC, or SLA guarantees — this is a portfolio-grade, single-operator build.

## 6. Users & Stakeholders (simulated)

- **Primary operator:** Anshul, acting as the analyst who clicks "run audit."
- **Approving stakeholder:** a simulated "data owner" persona (in the template this is a named contact who approves fixes by email) — for the portfolio build, this can be Anshul's own second inbox or a clearly labeled demo account.
- **Audience for the artifact:** recruiters/interviewers evaluating data-governance and AI-agent-orchestration skills for Data Analyst / FP&A / Business Analyst roles.

## 7. System Architecture

```
[Manual Trigger]                  [Form Trigger: Drag & Drop CSV/Excel]
      │                                       │
      │                                       ▼
      │                         [Code Node: Dynamic Schema Inference]
      │                                       │
      │                                       ▼
      │                         [Postgres: Auto-Create Table & Batch Load]
      │                                       │
      └──────────────────┬────────────────────┘
                         ▼
[Master Data Investigator Agent]  (LLM: Groq – Kimi K2)
  reads schema + samples data via Postgres Schema / Query tools
  → JSON array of issues: issue_id, category, description, sample_values, suggestion
      │
      ▼
[Filter: category == "Fixable with SQL"]───────► (else) [No-Op / logged for review]
      │
      ▼
[Gmail: "Are you available to review fixes?" — sendAndWait, Yes/No buttons]
      │ (No → stop run)
      ▼ (Yes)
[Loop Over Items — one issue at a time]
      │
      ▼
[Gmail: per-issue approval — description + proposed fix — sendAndWait]
      │ (rejected → skip, keep as "not fixed")
      ▼ (approved)
[Data Issue Fixer Agent]  (LLM: Gemini 2.5 Flash)
  generates UPDATE/DELETE SQL, executes via Query tool
  → {issue_id, status: resolved|failed, message, executed_sql}
      │
      ▼
[Merge: original issue list + fix results]
      │
      ▼
[Data Investigation Reporter Agent]  (LLM: Gemini 2.5 Flash)
  builds a formatted Google Doc (title, executive summary,
  fixed issues, discussion items), shares via Drive (view-only link)
  → {report_title, report_link}
      │
      ▼
[Gmail: final email with report link]
```

**Why this shape, not a single mega-agent:** splitting Investigator / Fixer / Reporter into three separately-prompted agents keeps each one's output contract small and strictly validated (JSON Schema per agent, Draft-07), which is what makes the "no markdown, no wrapping, exact keys" instructions in each system prompt actually enforceable — a single agent asked to detect-approve-fix-report in one pass would be far harder to keep schema-compliant and far riskier to let touch the database directly.

## 8. Agent Specifications

### 8.1 Master Data Investigator Agent
- **Model:** Groq — Kimi K2 (fast, cheap, good for a scan-and-classify task that doesn't need to write anything back)
- **Persona:** "Master Data Health Checker" — scans every reachable schema/table/column via a connected Postgres schema + query tool.
- **Checks for:** missing/NULL values in mandatory fields, placeholder tokens (`UNKNOWN`, `N/A`, `-`), inconsistent formats/casing/whitespace, mixed data types in a column, outliers, duplicate rows, referential integrity violations (orphaned keys), timestamp anomalies, precision/scale mismatches, schema drift.
- **Classifies each issue as:** `"Fixable with SQL"` or `"Needs Policy Establishment"`.
- **Output contract (strict JSON array, no markdown/wrapping):**
  ```json
  [{
    "issue_id": "ISSUE-001",
    "category": "Fixable with SQL",
    "description": "≤200 chars",
    "sample_values": ["1-5 example strings"],
    "suggestion": "≤200 chars"
  }]
  ```
  Empty array `[]` if nothing found.

### 8.2 Data Issue Fixer Agent
- **Model:** Gemini 2.5 Flash
- **Role:** SQL Generator & Executor — receives one approved issue at a time (`issue_id`, `category`, `description`, `sample_values`, `suggestion`), writes a single UPDATE or DELETE statement, and executes it through a connected query-executor tool.
- **Output contract:**
  ```json
  [{
    "issue_id": "ISSUE-001",
    "status": "resolved | failed",
    "message": "≤200 chars, human-readable outcome or error",
    "executed_sql": "the exact SQL attempted, even on failure"
  }]
  ```

### 8.3 Data Investigation Reporter Agent
- **Model:** Gemini 2.5 Flash
- **Role:** Report Generator — takes `{"data": [...]}` (merged issue + fix results) and produces a formatted Google Doc: title `"Database Health Check Report – <date>"`, one-line executive summary, "Fixed Issues" bullets (issue_id, description, executed_sql, with spacing rules), "Discussion Items" bullets (issue_id, description, suggestion), optional "Not Fixed Issues" section.
- **Delivery:** creates the doc via the Google Docs tool, shares it via Google Drive with "anyone with the link can view," and returns `{"report_title": "...", "report_link": "..."}`.

All three agents use an n8n **Structured Output Parser** node bound to a matching Draft-07 JSON Schema, so malformed LLM output fails fast instead of silently breaking downstream nodes.

## 9. Functional Requirements

| ID | Requirement | Acceptance criteria |
|---|---|---|
| FR-1 | Operator can trigger an audit on demand | Manual Trigger node starts the workflow; later swappable for a weekly/monthly schedule trigger |
| FR-2 | System scans the full AtliQ schema and returns a structured issue list | Investigator output validates against the issue JSON Schema; empty array is a valid "clean" result |
| FR-3 | Issues are split into auto-fixable vs. policy-needed | Filter node routes on `category == "Fixable with SQL"`; non-matching issues are logged, not silently dropped |
| FR-4 | No SQL runs without a human saying yes, twice | (a) one batch-level "are you available to review" email before any per-issue email goes out, (b) one per-issue approve/reject email before that issue's SQL executes |
| FR-5 | Rejected or skipped issues are still visible in the final report | Merge step preserves original issues regardless of fix outcome |
| FR-6 | Fixer agent only ever runs UPDATE/DELETE, never DDL | Enforced via the system prompt's explicit scope + a query-tool wrapper connected only to the target schema |
| FR-7 | Every executed fix is recorded with the exact SQL run | `executed_sql` field populated even on failure |
| FR-8 | Final report is human-readable and shareable without a login | Google Doc, view-only public link |
| FR-9 | Operator is notified when the report is ready | Final Gmail step with the doc link |
| FR-10 | Operator can onboard any arbitrary CSV/Excel via drag-and-drop | n8n Form Trigger accepts file; Code node infers schema, auto-creates table, batch-loads records, and triggers audit with zero manual SQL |

## 10. Data Model (Supabase / Postgres)

Load the five CSVs as-is (intentionally including the dirt) into a Supabase Postgres project — the setup docs in the resource pack literally walk through creating a project named **"AtliQ DB."** Suggested table shapes:

```sql
create table dim_customer (
  customer        text,
  market          text,
  platform        text,
  channel         text,
  customer_code   text primary key
);

create table dim_market (
  market    text primary key,
  sub_zone  text,
  region    text
);

create table dim_product (
  product_code  text primary key,
  division      text,
  segment       text,
  category      text,
  product       text,
  variant       text
);

create table fact_sales_monthly (
  date            date,
  division        text,
  category        text,
  product_code    text references dim_product(product_code),
  product         text,
  market          text references dim_market(market),
  platform        text,
  channel         text,
  customer_code   text references dim_customer(customer_code),
  customer_name   text,
  sold_quantity   text  -- deliberately text at load time; this is one of the issues the agent should catch
);

create table fact_forecast_monthly (
  date                date,
  division            text,
  category            text,
  product_code        text references dim_product(product_code),
  product             text,
  market              text references dim_market(market),
  platform            text,
  channel             text,
  customer_code       text references dim_customer(customer_code),
  customer_name       text,
  forecast_quantity   text
);
```

Load the raw files **without** the foreign-key constraints first (they'd fail immediately given the known orphaned codes/markets) — add the constraints only after the agent's fixes have run, or keep them off entirely and let the Investigator agent's "referential integrity" check do that job instead. Document this decision explicitly in the README; it's a good talking point ("I chose to let the agent surface FK violations rather than have the database reject the load silently").

## 11. Tech Stack

| Layer | Choice | Notes |
|---|---|---|
| Orchestration | n8n (self-hosted, local via Node.js/npm) | Per the resource pack's setup guide |
| Database | Supabase (hosted Postgres) | Free tier is sufficient for this dataset size |
| LLM — audit | Groq, Kimi K2 | Fast/cheap scan-and-classify |
| LLM — fix + report | Google Gemini 2.5 Flash | Two separate nodes/credentials, one per agent |
| Approval channel | Gmail node (`sendAndWait`, double approval type) | n8n's native human-in-the-loop email buttons |
| Report delivery | Google Docs + Google Drive nodes | Doc creation + "anyone with link" sharing |
| Schema validation | n8n Structured Output Parser + Draft-07 JSON Schema per agent | |

## 12. Non-Functional Requirements

- **Safety of writes:** the Fixer agent must only ever be able to reach the query-executor tool for UPDATE/DELETE — no DROP/ALTER/TRUNCATE in scope, and no execution without the per-issue approval email being explicitly approved.
- **Auditability:** every fix's exact SQL and outcome must be traceable in the final report; nothing should be fixed "invisibly."
- **Idempotency:** re-running the audit on an already-cleaned table should return `[]` (or a much shorter list) rather than re-flagging resolved issues — worth testing explicitly.
- **Cost control:** batching delay (6s between batches, already in the template) and using the cheaper Groq model for the high-volume scanning step keeps token spend low on a free/low-tier API budget.
- **Credential hygiene:** Supabase/Gemini/Groq/Google API keys stay in n8n credentials, never hardcoded in the workflow JSON that goes into the public repo — sanitize before pushing.

## 13. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| LLM-generated SQL is wrong or destructive | Human approval gate before every execution; scope the fixer to UPDATE/DELETE only; test on a Supabase branch/copy first, not production data |
| LLM output breaks JSON contract mid-run | Structured Output Parser + strict schema on every agent; fail loud rather than pass malformed data downstream |
| Publishing the real dataset publicly on GitHub | Use a synthetic/scrambled version of the AtliQ data for the public repo, same approach as the CarePlus project's synthetic sample dataset |
| Approval emails go to a real inbox during demoing/interviews | Use a dedicated demo Gmail account, not a personal/work inbox |
| Over-claiming this as "production-grade automation" in interviews | Be precise: this is a human-in-the-loop assisted governance workflow, not a fully autonomous system — and that's the correct design choice, worth defending as such |

## 14. Build Plan

1. **Environment setup** — Node.js + n8n local install; Supabase project ("AtliQ DB"); Gemini API key; Groq API key; Google Cloud project with Gmail, Docs, Drive APIs enabled. *(Setup guides already in the resource pack.)*
2. **Load the data** — create the five tables, import the raw CSVs as-is (dirt included).
3. **Import the n8n template** — bring in `data_governor_n8n_template.json`, reconnect all red (missing-credential) nodes to your own Supabase/Gemini/Groq/Google credentials.
4. **Validate the Investigator agent alone** — run it against the live DB, manually cross-check its output against the known-issues table in Section 2 above; tune the system prompt only if it's missing whole categories of issue.
5. **Wire and test the approval gate** — confirm the double-approval Gmail flow actually pauses the workflow and resumes correctly on Yes/No.
6. **Validate the Fixer agent on a handful of issues** — check `executed_sql` is sane before letting it run over the full list.
7. **Validate the Reporter agent** — confirm the Google Doc formatting (title/heading sizes, bullet spacing, SQL padding) matches the spec, and that sharing permissions are correct.
8. **Full end-to-end run** — one real pass from trigger to final email.
9. **Package for GitHub** — sanitize credentials out of the exported JSON, create a synthetic sample dataset, write the README (problem → architecture diagram → how to run → sample report screenshot/link → what you'd do differently in production), and a short LinkedIn post following the same pattern as prior projects.

## 15. Deliverables / Definition of Done

- [ ] Public GitHub repo: exported (sanitized) n8n workflow JSON, synthetic sample CSVs, README with architecture diagram and setup steps, sample report screenshot or a view-only link to a demo report.
- [ ] One successful end-to-end recorded run (screen recording or GIF is a strong README addition).
- [ ] README explicitly documents the known-issues catalog from Section 2 as "problems this system is designed to catch" — turns your own profiling work into project documentation.
- [ ] A short LinkedIn post, consistent with your existing project-announcement pattern.
- [ ] A two-minute verbal walkthrough you can give in an interview: problem → 3-agent architecture → why the approval gate is non-negotiable → what you'd change for a production version (e.g., scheduled trigger, DB-level audit log table, Slack instead of email for approvals).

## 16. Interview / Portfolio Narrative

Position this project as the governance/automation counterpart to your BI and modeling projects: Business Insights 360 shows you can build the dashboard *on top of* clean data; this project shows you understand *why* that data is rarely clean to begin with, and can design a controlled, auditable, human-approved system to fix it — directly relevant to BFSI/fintech data teams where ungoverned auto-fixes are a compliance risk, not just an engineering inconvenience. It also demonstrates AI-agent orchestration (multi-agent, tool-using, schema-constrained) beyond single-prompt chatbot demos, which is increasingly what Business Analyst / Data Analyst postings are starting to screen for.
