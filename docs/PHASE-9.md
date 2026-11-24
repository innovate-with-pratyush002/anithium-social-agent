# Phase 9 — Editorial Strategy and Content Opportunities

## Goal

Turn analyzed research into an actionable editorial shortlist before generating platform drafts. This phase is deterministic and does not call an AI provider, so it adds no Groq, OpenAI, or Gemini usage.

## Endpoint

Admin-protected:

    GET /api/v1/editorial/opportunities

Query parameters:

- `platforms`: repeatable; accepted values are `linkedin`, `instagram`, and `x`. Defaults to all three.
- `window_days`: research discovery window, 1–90; defaults to 14.
- `limit`: maximum returned opportunities, 1–100; defaults to 20.

Example:

    GET /api/v1/editorial/opportunities?platforms=linkedin&platforms=x&window_days=21&limit=15

Only research items that have completed AI analysis, remain in the `new` research status, and were discovered inside the requested window are considered.

## Opportunity scoring

The score is a transparent editorial heuristic:

    0.60 × relevance + 0.25 × research quality + 0.15 × freshness

- Missing relevance defaults to 0.0.
- Missing quality defaults to a neutral 0.5.
- Freshness decreases linearly from 1.0 at discovery to 0.0 at 30 days.
- Results are sorted by opportunity score, highest first.

The score is a prioritization aid, not a prediction of reach, engagement, or factual accuracy.

## Platform recommendations

Each eligible research item receives platform-specific editorial guidance:

- LinkedIn: practical implications for developers and technology teams; suggested format `insight_post`.
- Instagram: a visual, accessible explanation; suggested format `educational_carousel`.
- X: a concise verified takeaway with optional follow-up context; suggested format `short_post_or_thread`.

A platform is omitted when a content draft already exists for that research item and platform. This prevents the opportunity list from repeatedly recommending work already created. It does not delete, modify, approve, or publish any draft.

## Safety and cost

- No AI provider calls are made by this endpoint.
- No new database tables, columns, migrations, or environment variables are required.
- The endpoint is protected by the existing admin authorization dependency.
- The endpoint only recommends opportunities; content generation remains a separate explicit action.
- Generated content still starts in `draft` status and must pass the existing human approval workflow.
- The recommendations are templates, not claims about what an audience will engage with. Review source material before drafting or approving posts.

## Verification

    docker compose --profile scheduler up --build -d
    docker compose exec backend pytest -v
    docker compose exec backend ruff check --no-cache .

New tests cover platform-specific recommendations, draft deduplication, admin authorization, and query validation. They use a fake research analyzer and do not make live AI calls.
