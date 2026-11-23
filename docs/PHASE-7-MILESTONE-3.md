# Phase 7 — Milestone 3: Research Quality and Trend Signals

## Changes

- Explicit analysis lifecycle: pending, processing, completed, failed.
- Analysis attempts, last error, and analyzed timestamp are stored independently of relevance score.
- Failed analysis can be retried explicitly with retry_failed=true; an item is capped at three attempts.
- Row-level skip-locked selection prevents concurrent workers from selecting the same pending item.
- Ranked research now includes only completed analyses.
- RSS article URLs are normalized by removing common tracking parameters, fragments, default ports, and harmless trailing-slash variations before deduplication.
- A trend endpoint groups completed research by topic within a configurable discovery window. A topic is surfaced only after at least two items are found.

## API

POST /api/v1/research-intelligence/analyze

    {"max_items": 10, "retry_failed": false}

Set retry_failed=true to retry failed items that have fewer than three attempts. Optional research_item_ids restricts the batch.

GET /api/v1/research-intelligence/ranked?limit=20&offset=0

GET /api/v1/research-intelligence/trends?window_days=7&limit=10

All endpoints require an administrator bearer token.

## Migration

Run the migration after pulling and rebuilding:

    docker compose exec backend alembic upgrade head
    docker compose exec backend alembic current

Existing records with an intelligence metadata object and a relevance score are backfilled as completed. Older manually scored records without intelligence metadata remain pending and can be analyzed.

## Limitations

Trend signals are topic-frequency indicators, not claims that a topic is globally trending. They reflect only the research items collected by this installation. Source-quality weighting and semantic duplicate clustering are not included in this milestone.
