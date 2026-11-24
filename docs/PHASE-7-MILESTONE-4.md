# Phase 7 — Milestone 4: Research Quality Scoring and Source Reliability

## Goal

Add transparent quality signals so the research queue can distinguish topical relevance from the quality and provenance of a research item.

## Changes

- Each source has an administrator-managed reliability score from 0.0 to 1.0. New sources default to 0.7; this is a neutral starting assumption, not an externally verified reputation.
- Each research item has a deterministic quality score from 0.0 to 1.0 and a list of human-readable quality signals.
- Quality uses descriptive title, article URL, summary depth, available article text, publication recency, and source reliability.
- Quality is recalculated after AI research analysis, using the updated summary.
- Ranked research sorts by a combined score: 70% AI relevance and 30% research quality. Missing quality scores use a neutral 0.5 for sorting.
- Quality score and signals are exposed in research item responses.

## API changes

- Source create/update accepts `reliability_score` from 0.0 to 1.0; source read returns it.
- Research item read returns `quality_score` and `quality_signals`.
- Existing source records receive reliability score 0.7 during migration.
- Existing research items receive a null quality score and an empty quality-signal list; they are recalculated when analyzed again.

## Important interpretation

The quality score is a transparent metadata heuristic, not a fact-checking result or a guarantee that a source is trustworthy. Source reliability is an administrator-maintained setting and must be reviewed manually. The AI relevance score remains separate from quality.

## Migration

After pulling and rebuilding:

    docker compose exec backend alembic upgrade head
    docker compose exec backend alembic current

## Verification

    docker compose exec backend pytest -v
    docker compose exec backend ruff check --no-cache .
