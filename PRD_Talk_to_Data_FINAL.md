# Product Requirements Document (PRD)
## DataWhisper — Seamless Self-Service Intelligence
**Hackathon Theme 1 | Version 2.0 | April 2026**

---

## 1. Executive Summary

Business users today depend on data teams and SQL-savvy analysts to answer even simple questions like *"What was our revenue last month?"* This creates a bottleneck that slows decision-making and underutilises data assets.

**Talk to Data** eliminates this gap by providing a conversational AI assistant that allows any user — technical or non-technical — to interact with structured datasets using plain natural language. The system automatically translates user questions into validated SQL queries, executes them securely on the underlying data, and returns clear, human-readable answers with supporting tables and visualisations.

Built for a hackathon timeline (2–3 days), this MVP is designed to be clean, safe, and impressive — not over-engineered.

---

## 2. Problem Statement

| Problem | Impact |
|--------|--------|
| Non-technical users cannot write SQL queries | Business decisions are delayed or skipped |
| Data teams spend time answering repetitive ad-hoc queries | Engineering bandwidth is wasted |
| BI dashboards are fixed and cannot answer novel questions | Insight discovery is limited |
| Data is siloed across multiple tables / sources | Cross-domain questions go unanswered |
| Raw query access to databases creates security risk | Unsafe queries can corrupt or expose data |

**Core challenge:** Databases do not understand natural language. There must be a translation layer that bridges what a user asks in English and what the database understands as a query — while correctly mapping business terminology (e.g. "revenue", "top customers") to actual schema columns and tables — without compromising data safety.

---

## 3. Product Vision

> **"Ask your data a question in plain English — get a precise, context-aware answer instantly, without knowing SQL."**

The product will serve as a **self-service conversational analytics assistant** that is:
- **Domain-agnostic** — works with any dataset structure
- **Safe by default** — only read queries, auto-limited, keyword-blocked
- **Transparent** — shows the SQL it generated and explains it in plain English
- **Reusable** — semantic layer can be adapted for new datasets in minutes
- **Open and reproducible** — Apache 2.0, open-source tooling only
- **Lightweight** — runs on free-tier cloud or local environment

---

## 4. Target Users

| User Persona | Description | Key Need |
|---|---|---|
| Business Analyst | Reviews sales/ops data regularly | Ask follow-up questions without SQL |
| Product Manager | Monitors feature usage and metrics | Self-serve KPI lookup without data team |
| Operations Lead | Tracks inventory, logistics, SLAs | Instant cross-table insight |
| Student / Developer | Exploring datasets for learning/projects | Intuitive data exploration |

---

## 5. Scope

### In-Scope (MVP for Hackathon)
- Natural language to SQL conversion using free-tier LLM (Gemini, Groq/LLaMA, Mistral)
- SQL safety layer — SELECT-only enforcement, keyword blocking, auto-LIMIT
- Query explanation layer — SQL → plain English, "Explain this result" feature
- Semantic layer / schema config that maps business terms to database schema
- Single-turn and multi-turn (follow-up) conversational Q&A
- Query execution on Supabase (PostgreSQL) with Row Level Security (RLS)
- User authentication via Clerk (JWT-based sessions)
- Response rendering: text explanation + tabular data + optional chart
- Caching layer for NL→SQL and SQL→results
- Suggested starter queries and empty-state handling
- Evaluation system: predefined benchmark questions with accuracy tracking
- Logging and debug mode toggle
- Synthetic dataset (Faker or Kaggle open datasets)
- Web UI — Streamlit or Next.js frontend
- Public GitHub repository with Apache 2.0 license and full README

### Out-of-Scope (future rounds / post-hackathon)
- Real-time internet data fetching or live API integration
- PII or commercial data ingestion
- Enterprise SSO or advanced RBAC
- Voice interface
- Paid LLM tiers (all AI usage must be free-tier in hackathon)
- Multi-database federation

---

## 6. Functional Requirements

### 6.1 Conversational Interface (Chat UI)
- **FR-01:** User can type a question in English in a chat input box.
- **FR-02:** System displays the generated SQL query (collapsible) so users can verify it.
- **FR-03:** System displays the result as: (a) short text summary, (b) data table, (c) bar/line chart where applicable.
- **FR-04:** User can ask follow-up questions that refine the previous query using conversation context.
- **FR-05:** UI shows conversation history in a scrollable chat thread.
- **FR-06:** UI shows suggested starter queries on empty state (e.g., *"Try: What was total revenue last month?"*).
- **FR-07:** UI shows a loading spinner / skeleton state while query is being processed.
- **FR-08:** Each result includes an **"Explain this result"** button that returns a plain-English breakdown.

### 6.2 Natural Language to SQL Engine
- **FR-09:** System accepts a user question and generates a valid SQL query using a free-tier LLM (e.g., Google Gemini Flash, Groq LLaMA 3, Mistral via API).
- **FR-10:** System passes the semantic schema context (table names, column descriptions, relationships) to the LLM prompt for accurate query generation.
- **FR-11:** System validates generated SQL before execution (syntax check + safety check).
- **FR-12:** If generated SQL fails validation or execution, system retries **once** with a corrected prompt that includes the error message. On second failure, a user-friendly error message is shown with a suggested alternative query.

### 6.3 SQL Safety Layer
- **FR-13:** The system **only allows SELECT queries**. Any query not beginning with `SELECT` is rejected before execution.
- **FR-14:** Blocked keywords — the system scans generated SQL and **rejects** any query containing: `DROP`, `DELETE`, `UPDATE`, `INSERT`, `TRUNCATE`, `ALTER`, `CREATE`, `EXEC`, `EXECUTE`, `--` (comment injection).
- **FR-15:** System **auto-appends** `LIMIT {MAX_ROWS}` (default: 100) to all queries that do not already contain a LIMIT clause.
- **FR-16:** Basic SQL validation checks for balanced parentheses, valid table/column references from the schema, and absence of subquery injections.
- **FR-17:** All SQL validation happens **server-side** (backend), never client-side only.

### 6.4 Query Explanation Layer
- **FR-18:** After SQL is generated, system also generates a **plain-English explanation** of what the SQL does (e.g., *"This query sums total revenue grouped by product category for orders placed in the last 30 days"*).
- **FR-19:** The SQL explanation is shown below the collapsible SQL block by default.
- **FR-20:** User can click **"Explain this result"** to get an LLM-generated natural language summary of the returned data (e.g., *"Electronics had the highest revenue at ₹4.2L, up 12% from last month"*).
- **FR-21:** Explanation prompts are lightweight (short, focused) to stay within free-tier rate limits.

### 6.5 Semantic Layer
- **FR-22:** A YAML / JSON configuration file defines the semantic model:
  - Table names and descriptions
  - Column names, data types, and business-friendly descriptions
  - Relationships between tables (foreign keys)
  - Commonly used business terms and their mappings (e.g., `"revenue"` → `SUM(orders.amount)`)
- **FR-23:** This config is injected into the LLM prompt as structured context.
- **FR-24:** The semantic layer is human-editable so it can be adapted to any new dataset.

### 6.6 Query Execution and Data Layer
- **FR-25:** System connects to **Supabase (PostgreSQL)** as the primary data store.
- **FR-26:** Supabase **Row Level Security (RLS)** is enforced — each data table includes a `user_id` column; users can only access rows belonging to their own `user_id`.
- **FR-27:** Generated SQL is executed and results returned as a pandas DataFrame.
- **FR-28:** System limits result rows to a configurable maximum (default: 100) to prevent overload.
- **FR-29:** CSV / Excel file upload support as an alternate data source (loaded into an in-memory SQLite DB).

### 6.7 Authentication (Clerk + Supabase)
- **FR-30:** User authentication is handled by **Clerk** (email/password or OAuth). Clerk issues a signed JWT on login.
- **FR-31:** The JWT is passed in the `Authorization` header to the FastAPI backend on every API request.
- **FR-32:** The backend validates the JWT, extracts `user_id`, and passes it to Supabase queries.
- **FR-33:** Supabase RLS policies use `auth.uid()` to enforce per-user data isolation automatically.
- **FR-34:** Unauthenticated requests return `401 Unauthorized`.

### 6.8 Multi-turn Context
- **FR-35:** System maintains a session-level conversation history (last N turns, configurable).
- **FR-36:** Follow-up questions like *"Show me only the North region"* or *"Sort by revenue descending"* refine the previous query context.

### 6.9 Caching Layer
- **FR-37:** NL → SQL cache: identical natural language questions (normalised) return cached SQL without re-calling the LLM. Cache TTL: 1 hour (in-memory or Redis).
- **FR-38:** SQL → Results cache: identical SQL queries return cached DataFrame results without re-hitting the database. Cache TTL: 5 minutes.
- **FR-39:** Cache is scoped per `user_id` — one user's cached results are not shared with another.
- **FR-40:** Cache can be bypassed by appending `?refresh=true` to the API call (power users / debug).

### 6.10 Error Handling
- **FR-41:** All errors return user-friendly messages (never raw stack traces in the UI).
- **FR-42:** Error types and user messages:

| Error Type | User-Facing Message |
|---|---|
| SQL generation failure | *"I couldn't quite understand that. Try rephrasing — e.g., 'Show total sales for March 2025'."* |
| Unsafe SQL blocked | *"That type of query isn't supported. Try asking a question about your data instead."* |
| Database connection error | *"Having trouble reaching the database. Please try again in a moment."* |
| No results returned | *"No data matched your query. Try a broader date range or different filter."* |
| Rate limit hit (LLM) | *"The AI is a bit busy right now. Please wait a few seconds and try again."* |

- **FR-43:** On SQL execution failure, backend retries **once** with an error-correction prompt that includes the original SQL and the error message.
- **FR-44:** If retry also fails, system suggests 2–3 alternative queries the user might try.

### 6.11 Logging & Debugging
- **FR-45:** Backend logs the following for every request: timestamp, `user_id`, natural language input, generated SQL, validation result (pass/fail), execution time, row count returned.
- **FR-46:** Errors are logged with full stack traces server-side (never exposed to users).
- **FR-47:** A **debug mode** toggle (env var `DEBUG=true`) exposes additional internal state in the API response: raw LLM output, prompt used, cache hit/miss status.
- **FR-48:** Logs are written to `logs/app.log` (local) or a logging service in hosted deployment.

### 6.12 Evaluation System
- **FR-49:** A `tests/test_questions.json` file contains 20+ benchmark questions, each with: the natural language question, expected SQL (or expected result shape), and the tested table(s).
- **FR-50:** Running `python tests/run_eval.py` executes all benchmark questions and reports: % of queries that executed without error, % with correct result shape, and any regressions.
- **FR-51:** Accuracy target: **≥ 85%** on the predefined benchmark set.
- **FR-52:** Evaluation results are saved to `tests/eval_results.json` for comparison across commits.

### 6.13 Data
- **FR-53:** All datasets used are 100% synthetic / fake:
  - Generated using Python `Faker` library, OR
  - Sourced from clearly open, non-commercial Kaggle datasets
- **FR-54:** No personal data, PII, real customer records, or scraped internet data.
- **FR-55:** Seed script provided in repo to regenerate data (`generate_data.py`).

---

## 7. Non-Functional Requirements

| Requirement | Target |
|---|---|
| Response latency | < 5 seconds for typical queries (free-tier LLM) |
| SQL safety enforcement | 100% — no non-SELECT query ever reaches the database |
| Accuracy (semantic grounding) | ≥ 85% on predefined test question set |
| Cache hit rate (warm) | ≥ 60% for repeated queries |
| Dataset size support | Up to 100,000 rows in Supabase |
| Deployability | Must run locally via README; optionally hosted on Vercel / Render free tier |
| Code quality | PEP 8 compliant (Python), modular architecture, no hardcoded secrets |
| License | Apache 2.0, no incompatible third-party components |
| Repo size | Lightweight (< 50MB excluding data); dependencies in `requirements.txt` |
| Auth security | All API routes protected; JWT validated on every request |

---

## 8. Technical Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      User (Browser)                          │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                  Auth Layer — Clerk                          │
│  - Email / OAuth login                                       │
│  - Issues signed JWT on successful authentication            │
│  - JWT contains: user_id, email, session expiry             │
└──────────────────────────────┬───────────────────────────────┘
                               │ JWT in Authorization header
                               ▼
┌──────────────────────────────────────────────────────────────┐
│              Chat UI — Streamlit / Next.js                   │
│  - Chat thread display + conversation history                │
│  - Suggested starter queries (empty state)                  │
│  - Loading skeleton states                                   │
│  - Result renderer: text + table + chart                    │
│  - "Explain this result" button                             │
│  - Collapsible SQL block + plain-English explanation        │
└──────────────────────────────┬───────────────────────────────┘
                               │ REST API call + JWT
                               ▼
┌──────────────────────────────────────────────────────────────┐
│               Backend — Python / FastAPI                     │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  JWT Middleware                                        │  │
│  │  - Validates Clerk JWT on every request               │  │
│  │  - Extracts user_id → passes to downstream modules    │  │
│  └────────────────────────┬──────────────────────────────┘  │
│                           │                                  │
│  ┌────────────────────────▼──────────────────────────────┐  │
│  │  Cache Layer (in-memory / Redis)                      │  │
│  │  - NL→SQL cache (TTL: 1h, per user_id)               │  │
│  │  - SQL→Results cache (TTL: 5m, per user_id)          │  │
│  │  - Cache miss → continue pipeline                    │  │
│  └────────────────────────┬──────────────────────────────┘  │
│                           │                                  │
│  ┌────────────────────────▼──────────────────────────────┐  │
│  │  Conversation Manager                                  │  │
│  │  - Stores session history (last N turns)              │  │
│  │  - Provides context for follow-up questions           │  │
│  └────────────────────────┬──────────────────────────────┘  │
│                           │                                  │
│  ┌────────────────────────▼──────────────────────────────┐  │
│  │  Semantic Layer Loader                                 │  │
│  │  - Reads schema.yaml                                  │  │
│  │  - Builds structured LLM prompt context               │  │
│  └────────────────────────┬──────────────────────────────┘  │
│                           │                                  │
│  ┌────────────────────────▼──────────────────────────────┐  │
│  │  NL → SQL Engine (LLM Integration)                    │  │
│  │  - Free LLM API: Gemini Flash / Groq / Mistral        │  │
│  │  - Prompt: schema context + history + question        │  │
│  │  - Returns: raw SQL string                            │  │
│  └────────────────────────┬──────────────────────────────┘  │
│                           │                                  │
│  ┌────────────────────────▼──────────────────────────────┐  │
│  │  SQL Safety & Validation Module                       │  │
│  │  - Strips markdown fences, whitespace                 │  │
│  │  - Enforces SELECT-only                               │  │
│  │  - Blocks: DROP, DELETE, UPDATE, INSERT, etc.         │  │
│  │  - Auto-appends LIMIT if missing                      │  │
│  │  - Validates table/column names against schema        │  │
│  │  - REJECT → error handler → retry or user message    │  │
│  └────────────────────────┬──────────────────────────────┘  │
│                           │ Safe, validated SQL              │
│  ┌────────────────────────▼──────────────────────────────┐  │
│  │  Query Explanation Module                             │  │
│  │  - SQL → plain English summary (LLM call)             │  │
│  │  - "Explain this result" → data narrative (LLM call)  │  │
│  └────────────────────────┬──────────────────────────────┘  │
│                           │                                  │
│  ┌────────────────────────▼──────────────────────────────┐  │
│  │  Query Executor                                        │  │
│  │  - Connects to Supabase with service key              │  │
│  │  - Passes user_id for RLS enforcement                 │  │
│  │  - Executes validated SQL                             │  │
│  │  - Returns: pandas DataFrame                          │  │
│  └────────────────────────┬──────────────────────────────┘  │
│                           │                                  │
│  ┌────────────────────────▼──────────────────────────────┐  │
│  │  Response Formatter                                    │  │
│  │  - Generates text summary from results                │  │
│  │  - Serialises table for frontend                      │  │
│  │  - Creates chart config if numeric trend detected     │  │
│  └────────────────────────┬──────────────────────────────┘  │
│                           │                                  │
│  ┌────────────────────────▼──────────────────────────────┐  │
│  │  Logger                                                │  │
│  │  - Logs: user_id, NL input, SQL, exec time, rows      │  │
│  │  - Errors logged server-side with full trace          │  │
│  │  - Debug mode: exposes prompt + cache status          │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────────────┬───────────────────────────────┘
                               │ Supabase client (JWT / service key)
                               ▼
┌──────────────────────────────────────────────────────────────┐
│               Data Layer — Supabase (PostgreSQL)             │
│                                                              │
│  - All tables include user_id column                        │
│  - Row Level Security (RLS) policies enforced               │
│  - RLS policy: auth.uid() = user_id (read-only access)      │
│  - Synthetic retail dataset (customers, orders, products…)  │
│  - Schema defined in schema.yaml (semantic layer)           │
└──────────────────────────────────────────────────────────────┘
```

---

## 9. Authentication & Data Security Flow

### 9.1 Clerk + Supabase Integration

This project uses **Clerk for authentication** and **Supabase for data storage with Row Level Security**. They work together as follows:

```
User → Clerk Login → JWT Token → FastAPI Backend → Supabase RLS → Data Access
```

**Step-by-step flow:**

1. **User visits the app** and is redirected to the Clerk login screen (email/password or OAuth).
2. **Clerk authenticates the user** and issues a signed **JWT** containing `user_id`, `email`, and session expiry.
3. **Frontend stores the JWT** (Clerk SDK manages this automatically) and attaches it to every API request as `Authorization: Bearer <token>`.
4. **FastAPI middleware validates the JWT** on every incoming request using Clerk's public key. Invalid or expired tokens return `401 Unauthorized`.
5. **Extracted `user_id`** is passed to the Supabase client for all database operations.
6. **Supabase RLS policies** enforce that queries only return rows where `user_id = auth.uid()` — no user can accidentally access another user's data, even if they craft a direct SQL query.
7. **Supabase service role key** (stored in `.env`, never exposed to frontend) is used by the backend to execute queries on behalf of the authenticated user, with RLS still enforced.

### 9.2 Supabase RLS Policy Example

```sql
-- Enable RLS on the orders table
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- Policy: users can only SELECT their own rows
CREATE POLICY "Users can read own orders"
  ON orders
  FOR SELECT
  USING (auth.uid() = user_id);
```

All tables in the dataset (`customers`, `orders`, `order_items`, `products`, `regions`) include a `user_id` column and have equivalent RLS policies applied.

### 9.3 Environment Variables (`.env.example`)

```
# Clerk
CLERK_SECRET_KEY=sk_...
CLERK_PUBLISHABLE_KEY=pk_...

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=eyJ...

# LLM (pick one)
GEMINI_API_KEY=AIza...
GROQ_API_KEY=gsk_...

# App config
MAX_ROWS=100
CACHE_TTL_NL_SQL=3600
CACHE_TTL_RESULTS=300
DEBUG=false
```

---

## 10. SQL Safety Layer — Implementation Detail

The SQL Safety Module runs **before** any query reaches the database. It is a simple but critical guard.

```python
import re

BLOCKED_KEYWORDS = [
    "DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE",
    "ALTER", "CREATE", "EXEC", "EXECUTE", "--", ";"
]

def validate_sql(sql: str, max_rows: int = 100) -> tuple[str, str | None]:
    """
    Returns (cleaned_sql, error_message).
    error_message is None if validation passes.
    """
    sql = sql.strip().strip("```sql").strip("```").strip()

    # Rule 1: Must be a SELECT query
    if not sql.upper().startswith("SELECT"):
        return sql, "Only SELECT queries are allowed."

    # Rule 2: Block dangerous keywords
    for keyword in BLOCKED_KEYWORDS:
        if keyword.lower() in sql.lower():
            return sql, f"Query contains blocked keyword: {keyword}"

    # Rule 3: Auto-add LIMIT if missing
    if "LIMIT" not in sql.upper():
        sql = f"{sql.rstrip(';')} LIMIT {max_rows};"

    return sql, None
```

---

## 11. Error Handling & Retry Flow

```
NL Question
     │
     ▼
Generate SQL (LLM Call 1)
     │
     ▼
SQL Safety Validation
  ├── PASS → Execute Query
  │              ├── SUCCESS → Return results
  │              └── DB Error → Retry with error correction prompt (LLM Call 2)
  │                                 ├── SUCCESS → Return results
  │                                 └── FAIL → User-friendly error + suggested queries
  └── FAIL (unsafe SQL)
           └── User-friendly block message (no retry)
```

**Error correction prompt (LLM Call 2):**
```
The following SQL query failed with error: {error_message}

Original SQL:
{failed_sql}

Please fix the SQL query. Return ONLY the corrected SQL, nothing else.
```

---

## 12. Caching Layer — Implementation Detail

A lightweight two-level cache (in-memory `dict` for hackathon; swap to Redis for production).

| Cache Level | Key | TTL | Purpose |
|---|---|---|---|
| NL → SQL | `hash(user_id + normalised_question)` | 60 min | Avoid re-calling LLM for identical questions |
| SQL → Results | `hash(user_id + validated_sql)` | 5 min | Avoid re-hitting DB for same query |

```python
from functools import lru_cache
import hashlib, time

_cache: dict = {}

def cache_get(key: str):
    entry = _cache.get(key)
    if entry and time.time() < entry["expires"]:
        return entry["value"]
    return None

def cache_set(key: str, value, ttl: int):
    _cache[key] = {"value": value, "expires": time.time() + ttl}

def make_key(*parts) -> str:
    return hashlib.md5("|".join(str(p) for p in parts).encode()).hexdigest()
```

---

## 13. Query Explanation — LLM Prompts

### 13.1 SQL → Plain English (auto-generated with every query)

```
System: You are a data analyst assistant. Explain what the following SQL query does
in 1-2 plain English sentences. Be specific about tables, filters, and aggregations used.
Do NOT repeat the SQL. Do NOT use technical jargon.

SQL:
{generated_sql}

Explanation:
```

### 13.2 "Explain this result" (on user click)

```
System: You are a data analyst. Summarise the following query results in 2-3 sentences.
Highlight the most interesting number, trend, or outlier. Be specific and quantitative.

Original question: {user_question}
Query results (first 10 rows):
{result_sample}

Summary:
```

---

## 14. Recommended Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Frontend / UI | Streamlit (Python) or Next.js | Fastest to build; free deploy on Streamlit Cloud |
| Backend | Python + FastAPI | Clean REST API, easy async, Python ecosystem |
| Authentication | Clerk | Free tier, drop-in JWT auth, works with any frontend |
| LLM (free tier) | Google Gemini Flash or Groq (LLaMA 3) | Fast, free, capable text-to-SQL |
| Database | Supabase (PostgreSQL) | Free tier, built-in RLS, REST + Python client |
| Semantic layer config | YAML file | Human-readable, version-controllable |
| Caching | Python `dict` (in-memory) | Zero-dependency for hackathon; Redis-ready |
| Fake data generation | Python Faker + pandas | Easy synthetic data, fully reproducible |
| Charts | Plotly (via Streamlit) | Interactive, no extra cost |
| Hosting (optional) | Streamlit Community Cloud / Render | Free tier, one-click deploy |

---

## 15. Suggested Dataset: Retail Sales Intelligence

To keep scope manageable, the team should implement a single domain with a realistic schema.

**Recommended domain: Retail Sales**

```
Tables:
├── customers     (customer_id, user_id, name, region, segment, join_date)
├── products      (product_id, user_id, name, category, sub_category, unit_price)
├── orders        (order_id, user_id, customer_id, order_date, status)
├── order_items   (item_id, order_id, user_id, product_id, quantity, discount)
└── regions       (region_id, region_name, country)
```

> Note: `user_id` is included in all tables for Supabase RLS enforcement.

**Sample questions the system should answer:**
- "What is the total revenue for Q1 2025?"
- "Which product category had the highest sales last month?"
- "Show me the top 5 customers by total order value."
- "Compare revenue between North and South regions for 2024."
- "Which products are declining in sales over the last 3 months?"
- "What is the average order value by customer segment?"
- "How many orders were placed in January vs February?"
- "Which customer segment has the lowest average discount?"

All data is 100% synthetic, generated via Faker + a `generate_data.py` seed script in the repo.

---

## 16. Semantic Layer Example (`schema.yaml`)

```yaml
tables:
  - name: orders
    description: "Records of all customer purchase orders"
    columns:
      - name: order_id
        description: "Unique identifier for each order"
      - name: customer_id
        description: "References the customer who placed the order"
      - name: order_date
        description: "Date the order was placed (YYYY-MM-DD)"
      - name: status
        description: "Order status: pending, completed, cancelled"

  - name: order_items
    description: "Individual line items within each order"
    columns:
      - name: quantity
        description: "Number of units purchased"
      - name: discount
        description: "Discount applied as a decimal (0.0 to 1.0)"

  - name: products
    description: "Product catalogue with pricing"
    columns:
      - name: unit_price
        description: "Price per unit in INR"
      - name: category
        description: "High-level product category (Electronics, Clothing, etc.)"

  - name: customers
    description: "Registered customer profiles"
    columns:
      - name: region
        description: "Geographic region: North, South, East, West"
      - name: segment
        description: "Customer segment: Consumer, Corporate, SMB"

business_terms:
  revenue: "SUM(order_items.quantity * products.unit_price * (1 - order_items.discount))"
  top_customers: "customers ranked by total revenue DESC"
  last_quarter: "order_date BETWEEN DATE('now', '-3 months') AND DATE('now')"
  last_month: "order_date BETWEEN DATE('now', '-1 month') AND DATE('now')"

relationships:
  - from: orders.customer_id
    to: customers.customer_id
  - from: order_items.order_id
    to: orders.order_id
  - from: order_items.product_id
    to: products.product_id
```

---

## 17. LLM Prompt Structure

```
System:
You are a SQL expert working with PostgreSQL. Translate the user's natural language
question into a valid SQL SELECT query.

Rules:
- Use ONLY the tables and columns defined in the schema below.
- ONLY write SELECT queries. Never write DROP, DELETE, UPDATE, or INSERT.
- Do NOT add a LIMIT clause — it will be added automatically.
- Return ONLY the SQL query, with no explanation, no markdown, no backticks.

Schema:
{semantic_layer_context}

Business terms:
{business_terms}

Conversation history (last 3 turns):
{last_3_turns}

User question:
{user_question}

SQL:
```

---

## 18. UX States & Suggested Queries

### 18.1 Empty State
When no conversation has started, show:
```
💬 Ask anything about your data. Here are some ideas:

• "What was total revenue last month?"
• "Show top 5 products by sales this quarter"
• "Which region has the lowest average order value?"
• "How many orders were cancelled in 2025?"
```

### 18.2 Loading State
- Show a spinner with text: *"Generating query…"* → *"Running query…"* → *"Formatting results…"*
- Use a skeleton table placeholder while results load.

### 18.3 No Results State
```
🔍 No data found for your query.

The query ran successfully, but returned 0 rows. You might try:
• A broader date range
• Checking spelling of filters (e.g., region names)
• [Try a suggested question]
```

---

## 19. Repository Structure

```
talk-to-data/
├── README.md                    # Golden source documentation
├── LICENSE                      # Apache 2.0
├── requirements.txt             # Python dependencies
├── .env.example                 # Template for all env vars (never commit .env)
├── .gitignore
│
├── data/
│   ├── generate_data.py         # Faker-based synthetic data generator
│   ├── schema.yaml              # Semantic layer definition
│   └── sample_data.sql          # Pre-generated SQL dump (small sample)
│
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── auth.py                  # Clerk JWT validation middleware
│   ├── llm_client.py            # LLM API integration (Gemini / Groq)
│   ├── sql_engine.py            # Query generation + execution
│   ├── sql_safety.py            # SQL validation + safety enforcement
│   ├── sql_explainer.py         # SQL → plain English + result explanation
│   ├── semantic_layer.py        # YAML loader + prompt builder
│   ├── conversation.py          # Session history manager
│   ├── cache.py                 # NL→SQL and SQL→Results cache
│   ├── formatter.py             # Response text + chart builder
│   └── logger.py                # Structured logging + debug mode
│
├── frontend/
│   └── app.py                   # Streamlit UI (or Next.js in /frontend/)
│
├── logs/
│   └── app.log                  # Runtime logs (gitignored)
│
└── tests/
    ├── test_sql_safety.py        # Unit tests for safety module
    ├── test_sql_engine.py        # Unit tests for query generation
    ├── test_questions.json       # 20+ benchmark NL questions + expected SQL
    └── run_eval.py               # Evaluation runner → prints accuracy report
```

---

## 20. Evaluation System

### 20.1 Benchmark File (`test_questions.json`)

```json
[
  {
    "id": "Q01",
    "question": "What is the total revenue for Q1 2025?",
    "expected_tables": ["orders", "order_items", "products"],
    "expected_aggregation": "SUM",
    "should_succeed": true
  },
  {
    "id": "Q02",
    "question": "Show top 5 customers by order value",
    "expected_tables": ["customers", "orders", "order_items"],
    "expected_limit": 5,
    "should_succeed": true
  },
  {
    "id": "Q_SAFETY_01",
    "question": "Drop the orders table",
    "expected_blocked": true,
    "should_succeed": false
  }
]
```

### 20.2 Evaluation Metrics

| Metric | Definition | Target |
|---|---|---|
| Execution success rate | % of valid questions that return results without error | ≥ 90% |
| Table accuracy | % of queries referencing the correct expected tables | ≥ 85% |
| Safety block rate | % of unsafe questions correctly blocked | 100% |
| Avg response time | Mean end-to-end latency across all test questions | < 5s |

---

## 21. README Requirements (Judging Checklist)

The `README.md` must include:

- [ ] **Project title and one-line description**
- [ ] **Problem statement** (2–3 sentences, non-technical)
- [ ] **Solution overview** (how it works, with architecture diagram or ASCII art)
- [ ] **Features list** (bullet points)
- [ ] **Tech stack** (table format)
- [ ] **Installation steps** (`git clone`, `pip install`, env setup, run DB, run app)
- [ ] **Usage with examples** (3–5 sample questions with screenshots)
- [ ] **Data** (how to regenerate fake data with `generate_data.py`)
- [ ] **Auth setup** (Clerk + Supabase RLS configuration notes)
- [ ] **Hosted demo link** (if deployed on Streamlit Cloud / Render)
- [ ] **License badge** (Apache 2.0)
- [ ] **Contributing / DCO note**

---

## 22. Judging Criteria Alignment

| Judging Factor | How This PRD Addresses It |
|---|---|
| **Innovation** | Conversational NL→SQL over structured data with SQL explanation layer |
| **Technical depth** | LLM integration, semantic YAML layer, SQL safety module, Clerk+Supabase auth with RLS, caching |
| **Security** | SELECT-only enforcement, JWT auth, per-user RLS, keyword blocking |
| **Code quality** | PEP 8, modular structure, no secrets, Apache 2.0, full test suite |
| **Reproducibility** | Full setup in README, seed data script, free-tier hosting |
| **README clarity** | Golden source with all required sections |
| **Usability** | Non-technical users ask questions in English; empty states, loading states, error guidance |
| **Data compliance** | 100% fake data, no PII, no commercial datasets |

---

## 23. Hackathon Round Deliverables

| Round | What to Submit | Due |
|---|---|---|
| **Round 2 (current)** | Public GitHub repo with README + initial code structure + `schema.yaml` | 12 April 2026 |
| **Round 3 (if shortlisted)** | Full working prototype + 5-min demo video (uploaded via Unstop link) | TBD after Round 2 results |
| **Final Round** | Online Zoom presentation + live demo + Q&A with judges | TBD |

---

## 24. Team Checklist (Before Submission)

- [ ] GitHub repo is **public**
- [ ] Each team member uses **one personal email** linked to GitHub
- [ ] `LICENSE` file contains Apache 2.0 text
- [ ] `.env` is in `.gitignore`; only `.env.example` is committed
- [ ] No plagiarised or incompatible third-party code
- [ ] `requirements.txt` lists all Python packages with pinned versions
- [ ] README covers all sections in Section 21 above
- [ ] `generate_data.py` works to recreate the database from scratch
- [ ] Clerk + Supabase RLS configured and tested
- [ ] SQL safety layer tested with at least 5 unsafe inputs
- [ ] Evaluation script (`run_eval.py`) runs and produces an accuracy report
- [ ] At least one team member has verified the app runs from a clean clone
- [ ] Hosted demo link is live and accessible (Streamlit Cloud / Render)

---

*PRD prepared for Hackathon Theme 1: Talk to Data | Version 2.0 | April 2026*
