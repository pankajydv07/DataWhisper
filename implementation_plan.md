# DataWhisper Hackathon Upgrade Plan

## Summary
Current state: the repo is a good retail analytics MVP, not yet a full hackathon solution. It already has auth, chat sessions, NL-to-SQL, SQL safety checks, result summarization, and chart/table rendering, but it is still optimized for one fixed retail schema and one generic query path.

This plan targets a hackathon-complete demo on a curated dataset first, with extension points for future arbitrary-dataset onboarding.

Chosen defaults:
- Scope: curated demo dataset, not arbitrary upload in this implementation pass
- Trust model: pragmatic grounding, not formal statistical validation
- Ambiguity handling: ask a follow-up when ambiguity would materially change the answer

## Key Changes
- Add explicit query intents: `change`, `compare`, `breakdown`, `summarize`, `general`, `clarify`
- Route `/api/query` through intent-aware handlers while keeping one public entrypoint
- Expose trust metadata in responses: source tables, metric definitions, assumptions, and clarification questions
- Add `GET /api/metrics` for the semantic metric dictionary
- Support comparison, breakdown, and leadership-style summary outputs in the frontend
- Tighten SQL validation around approved tables and authenticated `user_id` scoping

## Public Interface Changes
- `QueryResponse` adds `intent`, `data_sources`, `metric_definitions`, `assumptions`, `clarification_question`, and `comparison`
- `ChartPayload.type` expands to `bar`, `line`, `pie`, and `stacked_bar`
- New endpoint: `GET /api/metrics`

## Test Plan
- Extend backend unit tests for intent classification, time phrase resolution, SQL validation, source extraction, and response shaping
- Preserve and rerun the existing backend tests
- Verify frontend rendering for trust badges, clarifications, comparison outputs, and expanded chart types

## Assumptions
- This implementation optimizes for a strong judged demo on curated retail data
- “Verified insights” means grounded in query results, explicit metric definitions, and visible source references
- Formal significance testing is out of scope for this pass
