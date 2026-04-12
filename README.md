# DataWhisper

DataWhisper is a conversational analytics app for a curated retail dataset. Users can ask natural-language questions and get intent-aware answers with plain-English summaries, source transparency, metric definitions, tables, and charts.

The current implementation is optimized for a hackathon demo around three pillars:
- Clarity: non-technical summaries and clarification prompts for ambiguous questions
- Trust: source-table citations, metric dictionary, explicit assumptions, and user-scoped queries
- Speed: one chat workflow, response caching, and compact visual output

## What It Supports

DataWhisper recognizes these query modes:
- `change`: "Why did revenue drop last month?"
- `compare`: "Compare North vs South region this month"
- `breakdown`: "Break down sales by category"
- `summarize`: "Give me a weekly summary for customer metrics"
- `general`: regular analytics questions
- `clarify`: follow-up prompt when the question is too ambiguous to answer safely

Each answer can include:
- plain-English summary
- SQL explanation
- source-table citation
- metric definition references
- assumptions used to resolve defaults
- comparison payloads for side-by-side reads
- table and chart output
- execution-time and cache metadata

## Architecture

```txt
User -> Clerk auth -> Next.js chat UI -> FastAPI API
     -> intent classification + semantic layer + Groq NL-to-SQL
     -> SQL safety + user-scope validation
     -> Supabase/Postgres
     -> summary + trust metadata + table/chart response
```

## Tech Stack

| Layer | Technology |
| --- | --- |
| Frontend | Next.js 14 App Router, Tailwind CSS, Clerk, Recharts |
| Backend | FastAPI, Pydantic, pandas, psycopg |
| Auth | Clerk JWT |
| Database | Supabase PostgreSQL with user-scoped rows |
| LLM | Groq OpenAI-compatible Chat Completions API |
| Cache | In-memory Python TTL cache |

## Project Structure

```txt
backend/   FastAPI API, intent helpers, semantic layer, SQL safety, tests
frontend/  Next.js app, chat UI, metric dictionary, comparison views
logs/      Runtime logs, ignored except .gitkeep
```

## Setup

1. Create backend environment:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

2. Fill `.env` with Clerk, Groq, and Supabase values:

```env
CLERK_JWKS_URL=https://your-clerk-domain/.well-known/jwks.json
CLERK_ISSUER=https://your-clerk-domain
GROQ_API_KEY=gsk_xxx
GROQ_MODEL=llama-3.3-70b-versatile
SUPABASE_DB_URL=postgresql://postgres.project-ref:password@aws-1-region.pooler.supabase.com:5432/postgres
SEED_USER_ID=user_xxx
FRONTEND_ORIGIN=http://localhost:3000
MAX_ROWS=100
CACHE_TTL_NL_SQL=3600
CACHE_TTL_RESULTS=300
```

3. Create frontend environment:

```bash
cd frontend
npm install
copy .env.local.example .env.local
```

4. Run the backend from the repo root:

```bash
uvicorn backend.main:app --reload
```

5. Run the frontend:

```bash
cd frontend
npm run dev
```

## Data Model

The demo uses four retail tables:
- `customers`
- `products`
- `orders`
- `order_items`

The semantic layer in [backend/data/schema.yaml](/d:/DataWhisper/backend/data/schema.yaml:1) defines:
- tables and relationships
- business terms
- metric definitions
- source tables for each metric
- default time grains and synonyms

Use the Supabase Session Pooler connection string if your network is IPv4-only. The direct `db.<project-ref>.supabase.co` host may be IPv6-only and fail DNS or connectivity from local machines.

Enable RLS and add read policies for your chosen auth integration. The backend also enforces explicit authenticated `user_id` scoping because direct database connections can bypass RLS depending on role and policy setup.

## Generate Synthetic Data

```bash
python backend/data/generate_data.py
```

The script creates the retail tables when missing, replaces rows for `SEED_USER_ID`, inserts Faker data, and writes `backend/data/sample_seed.sql`.

## API

### `POST /api/query`

Request:

```json
{
  "question": "Why did revenue drop last month?",
  "session_id": "abc123"
}
```

Response shape:

```json
{
  "session_id": "abc123",
  "session_title": "Why did revenue drop last month?",
  "intent": "change",
  "sql": "SELECT ... LIMIT 100",
  "sql_explanation": "This query compares completed-order revenue...",
  "result_summary": "Revenue declined... Based on orders, order_items, products.",
  "table": { "columns": ["region", "revenue"], "rows": [] },
  "chart": { "type": "pie", "x": "region", "y": "revenue", "series": [] },
  "comparison": {
    "columns": ["period", "revenue"],
    "rows": [],
    "focus": "revenue"
  },
  "data_sources": ["orders", "order_items", "products"],
  "metric_definitions": [
    {
      "key": "revenue",
      "label": "Revenue",
      "definition": "Total completed-order sales after discount.",
      "formula": "SUM(...)",
      "source_tables": ["orders", "order_items", "products"],
      "default_time_grain": "month"
    }
  ],
  "assumptions": [],
  "clarification_question": null,
  "cached": false,
  "execution_time_ms": 820
}
```

Clarification responses use the same endpoint and return `intent: "clarify"` with `clarification_question` populated.

### `GET /api/metrics`

Returns the semantic metric dictionary used by the chat UI trust panel.

## Safety Rules

- Strip markdown SQL fences from model output
- Reject anything not starting with `SELECT`
- Block mutating keywords, comments, semicolons, and unsupported query patterns
- Restrict queries to approved demo tables
- Auto-append `LIMIT 100` when missing
- Require generated SQL to include authenticated `user_id` predicates for referenced tables

## Suggested Questions

- Why did revenue drop last month?
- Compare North vs South region this month
- Break down sales by category
- Give me a weekly summary for customer metrics
- Show top 5 customers by order value

## Tests

Backend tests:

```bash
pytest backend/tests -q
```

Frontend production build:

```bash
npm --prefix frontend run build
```

Evaluation calls Groq and requires `GROQ_API_KEY`:

```bash
python backend/tests/run_eval.py
```

## Railway Deployment

Deploy this repo as two Railway services:

1. Backend service
   - Root directory: repo root
   - Uses [railway.json](/d:/DataWhisper/railway.json) and [nixpacks.toml](/d:/DataWhisper/nixpacks.toml)
   - Required env vars:
     - `CLERK_JWKS_URL`
     - `CLERK_ISSUER`
     - `GROQ_API_KEY`
     - `GROQ_MODEL`
     - `SUPABASE_DB_URL`
     - `MAX_ROWS`
     - `CACHE_TTL_NL_SQL`
     - `CACHE_TTL_RESULTS`
     - `DEBUG`
     - `FRONTEND_ORIGIN`

2. Frontend service
   - Root directory: `frontend`
   - Uses [frontend/railway.json](/d:/DataWhisper/frontend/railway.json) and [frontend/nixpacks.toml](/d:/DataWhisper/frontend/nixpacks.toml)
   - Required env vars:
     - `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
     - `NEXT_PUBLIC_API_URL`
     - `CLERK_SECRET_KEY`

Set `NEXT_PUBLIC_API_URL` to the deployed Railway backend URL and set backend `FRONTEND_ORIGIN` to the deployed Railway frontend URL.
