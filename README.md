# DataWhisper

DataWhisper is a conversational analytics app that turns natural language questions into safe PostgreSQL queries, executes them against Supabase, and returns summaries, tables, and charts.

## Architecture

```txt
User -> Clerk auth -> Next.js chat UI -> FastAPI API -> Groq NL-to-SQL
     -> SQL safety checks -> Supabase/Postgres -> summary/table/chart response
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
backend/   FastAPI API, Groq client, SQL safety, semantic layer, tests
frontend/  Next.js app, Clerk auth, chat UI, tables, charts
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
SUPABASE_DB_URL=postgresql://...
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

## Supabase Tables

```sql
CREATE TABLE customers (
  customer_id uuid PRIMARY KEY,
  user_id text NOT NULL,
  name text NOT NULL,
  region text NOT NULL,
  segment text NOT NULL,
  join_date date NOT NULL
);

CREATE TABLE products (
  product_id uuid PRIMARY KEY,
  user_id text NOT NULL,
  name text NOT NULL,
  category text NOT NULL,
  sub_category text NOT NULL,
  unit_price numeric NOT NULL
);

CREATE TABLE orders (
  order_id uuid PRIMARY KEY,
  user_id text NOT NULL,
  customer_id uuid NOT NULL REFERENCES customers(customer_id),
  order_date date NOT NULL,
  status text NOT NULL
);

CREATE TABLE order_items (
  item_id uuid PRIMARY KEY,
  order_id uuid NOT NULL REFERENCES orders(order_id),
  user_id text NOT NULL,
  product_id uuid NOT NULL REFERENCES products(product_id),
  quantity integer NOT NULL,
  discount numeric NOT NULL
);
```

Enable RLS and add read policies for your chosen auth integration. This scaffold also enforces explicit `user_id` scoping server-side because direct service-role database connections can bypass Supabase RLS.

## Generate Synthetic Data

```bash
python backend/data/generate_data.py
```

The script writes `backend/data/sample_seed.sql`. Set `SEED_USER_ID` to match the Clerk `sub` value you want to test with.

## API

`POST /api/query`

```json
{
  "question": "What was total revenue last month?",
  "session_id": "abc123"
}
```

Response:

```json
{
  "sql": "SELECT ... LIMIT 100",
  "sql_explanation": "This query sums completed order revenue...",
  "result_summary": "Revenue last month was INR 421300...",
  "table": { "columns": ["month", "revenue"], "rows": [] },
  "chart": { "type": "bar", "x": "month", "y": "revenue" },
  "cached": false,
  "execution_time_ms": 820
}
```

## Safety Rules

- Strip markdown SQL fences from model output.
- Reject anything not starting with `SELECT`.
- Block mutating keywords, comments, and semicolons.
- Auto-append `LIMIT 100` when missing.
- Require generated SQL to include the authenticated `user_id`.

## Suggested Questions

- What was total revenue last month?
- Show top 5 customers by order value
- Which product category has the highest sales?
- Compare revenue by region for 2025
- How many orders were cancelled this quarter?

## Tests

```bash
pytest
```

Evaluation calls Groq and requires `GROQ_API_KEY`:

```bash
python backend/tests/run_eval.py
```
