# DataWhisper – Hackathon Gap Analysis & Implementation Plan

## What the Hackathon Expects

The challenge has **3 pillars** and **4 core analytical capabilities**:

| Pillar | Requirement |
|---|---|
| **Clarity** | Answers simple enough for non-experts, no jargon |
| **Trust** | Clear definitions, consistent metrics, source transparency |
| **Speed** | Near-instant responses, no complex workflows |

| Capability | What it means |
|---|---|
| **1. Understand what changed** ("Why did revenue drop?") | Identify drivers, highlight most influential categories, explain in everyday language, reference data sources |
| **2. Compare** ("This week vs last week", "Region A vs B") | Interpret comparison intent, consistent metrics, visual + text output, handle ambiguous time phrases |
| **3. Breakdown/Decompose** ("What makes up total sales?") | Decompose by region/category/product/channel, surface outliers & concentration, table + narrative |
| **4. Summarize** ("Give me a weekly summary") | Scan for trends/anomalies, concise digest, avoid noise, source references, leadership-friendly |

---

## Gap Analysis — What's Missing

### ❌ MISSING: Intent Detection & Query Classification
**Required by:** All 4 capabilities  
The system currently sends every question through a single NL→SQL pipeline with no understanding of *what type* of query the user is asking. There is no intent classifier to route between "change", "compare", "breakdown", "summarize" flows.

### ❌ MISSING: Change/Driver Analysis (Capability #1)
- No endpoint or logic to detect a "why did X change?" question
- No driver identification (which dimension—region/product/channel—caused the change)
- No percentage-change calculation between periods
- The result_summary prompt is generic; it doesn't say **why** something changed

### ❌ MISSING: Structured Comparison (Capability #2)
- No time comparison logic ("this week vs last week", "Q1 vs Q2")
- Ambiguous time phrases like "this month" or "last cycle" only handled partially via `business_terms` in schema.yaml — not dynamically parsed
- No side-by-side comparison output (only a table is returned)
- No statistically relevant difference highlighting

### ❌ MISSING: Breakdown/Decomposition (Capability #3)
- No decomposition endpoint
- No logic to auto-detect the best breakdown dimension (region/category/channel)
- No outlier/concentration detection
- Formatter only picks one chart type (bar/line) — no pie/treemap for composition

### ❌ MISSING: Periodic Summarization (Capability #4)
- No `/api/summary` or scheduled summary endpoint
- No anomaly/trend detection logic across time periods
- No digest format (leadership-friendly output)
- No "avoid noise" filtering — all rows are returned

### ❌ MISSING: Source Transparency (Trust Pillar)
- The `sql_explanation` field exists but is only shown in the SQL block (collapsed)
- There is no **"data source" or "based on X rows from Y table"** citation in the main answer
- No metric definition display (e.g., "Revenue = quantity × unit_price × (1 - discount)")

### ❌ MISSING: Metric Dictionary / Semantic Layer UI (Trust Pillar)
- `schema.yaml` has `business_terms` but these are never shown to the user
- No way for user to see "what does revenue mean in this system?"

### ❌ MISSING: Ambiguous Query Handling (Clarity Pillar)
- No clarification flow when the question is vague
- No graceful prompt like "Did you mean this week or this month?"

### ❌ MISSING: Execution-time & Source Badge on UI (Speed + Trust)
- `execution_time_ms` exists in the backend response but is NOT displayed in the frontend
- No "cached" badge displayed to user

### ⚠️ PARTIAL: Result Summary
- `summarize_result` exists but uses a generic prompt — doesn't detect trends, anomalies, biggest movers, or explain *why*

### ⚠️ PARTIAL: Chart Types
- Only `bar` and `line` are supported — decomposition queries need `pie` or stacked charts

---

## Proposed Changes

### Backend

#### [MODIFY] `backend/llm_client.py`
- Add `classify_intent()` function — returns one of: `change`, `compare`, `breakdown`, `summarize`, `general`
- Add `analyze_change()` — enhanced prompt that identifies root cause / driver of a change
- Add `generate_comparison_sql()` — two-period SQL generation with consistent metric definitions
- Add `generate_breakdown_sql()` — decompose by most relevant dimension
- Add `generate_summary()` — trend + anomaly scan prompt

#### [MODIFY] `backend/sql_explainer.py`
- Enhance `summarize_result()` to produce change-aware, breakdown-aware, trend-aware narratives
- Add `cite_sources()` — appends "Based on X rows from orders, products" to every response

#### [MODIFY] `backend/formatter.py`
- Add `pie` and `stacked_bar` as chart types
- Add outlier detection in `infer_chart()`

#### [MODIFY] `backend/models.py`
- Add `intent` field to `QueryResponse`
- Add `data_sources` field (list of table names used)
- Add `metric_definitions` field (relevant business terms used)
- Add `comparison` field for side-by-side comparison data

#### [MODIFY] `backend/main.py`
- Add intent detection before SQL generation
- Route to appropriate handler based on intent
- Add `/api/metrics` endpoint — returns the metric dictionary from schema
- Add `/api/summary` endpoint — weekly/monthly digest

#### [MODIFY] `backend/data/schema.yaml`
- Add `this_week`, `last_week`, `wow` (week-over-week) business terms
- Add `channel` column concept

### Frontend

#### [MODIFY] `components/ChatMessage.tsx`
- Display `execution_time_ms` badge
- Display "cached" badge when response is cached
- Display `data_sources` citation ("Based on: orders, products, customers")
- Display metric definitions inline when used

#### [NEW] `components/MetricDictionary.tsx`
- Sidebar panel showing all business term definitions from `/api/metrics`

#### [NEW] `components/ComparisonView.tsx`
- Side-by-side comparison table with delta highlighting (green/red)

#### [NEW] `components/InsightBadge.tsx`
- Intent badge: shows query type (Change Analysis / Comparison / Breakdown / Summary)

#### [MODIFY] `components/ResultChart.tsx`
- Add `pie` chart support via recharts
- Add `stacked_bar` support

#### [MODIFY] `app/chat/page.tsx`
- Add metric dictionary toggle in sidebar
- Show insight badge per message
- Add "Weekly Summary" quick action button

---

## Verification Plan

### Automated
- Run backend: `uvicorn backend.main:app --reload`
- Test all 4 query types via `/api/query`
- Test `/api/metrics` endpoint

### Manual
- Ask "Why did revenue drop last month?" → should return driver analysis
- Ask "Compare North vs South region" → should return side-by-side
- Ask "Break down sales by category" → should return decomposition + pie chart
- Ask "Give me a weekly summary" → should return digest with anomaly callouts
- Check every response shows data source citation
- Check execution time badge visible in UI
- Open metric dictionary to see "revenue" definition
