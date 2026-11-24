# Phase 7 — Milestone 5: Scheduled Research Pipeline

## Goal

Run RSS collection and AI research analysis on a schedule without keeping scheduler state inside the API process.

## Architecture

- The FastAPI backend remains an API-only process.
- A separate `research-worker` container runs APScheduler.
- The worker uses the same application services and PostgreSQL database as the API.
- RSS ingestion and AI analysis run as separate interval jobs.
- Both jobs run once immediately after worker startup, then repeat at their configured intervals.
- Each job allows only one active instance and coalesces missed executions.
- The existing analysis retry limit remains three attempts. Failed items are retried only when their analysis request opts into retrying; the scheduled job does not enable retries automatically.
- The worker does not approve, schedule, or publish social content.

## Configuration

Add or update these values in the private local `.env` file:

```dotenv
RESEARCH_INGESTION_INTERVAL_MINUTES=60
RESEARCH_ANALYSIS_INTERVAL_MINUTES=30
RESEARCH_INGESTION_MAX_ITEMS_PER_SOURCE=20
RESEARCH_ANALYSIS_MAX_ITEMS=10
```

Intervals must be between 5 and 1440 minutes. Batch limits are validated by application settings.

## Start the worker

The worker is opt-in so it cannot unexpectedly consume AI-provider quota during ordinary development:

```bash
docker compose --profile scheduler up --build -d
docker compose ps
docker compose logs -f research-worker
```

To run only the API and database, continue using:

```bash
docker compose up --build -d
```

Stop the scheduled worker while keeping the API and database running:

```bash
docker compose stop research-worker
```

## Operational notes

- The first ingestion and analysis jobs run immediately after worker startup.
- Configure a valid selected AI provider key before enabling the worker. If the provider is not configured, the analysis job logs the failure and the next scheduled run can try again.
- Newly ingested items are analyzed by subsequent analysis runs. Ingestion and analysis are independent jobs, so a small delay between them is expected.
- Keep exactly one scheduler worker replica until a distributed scheduler lock is introduced. Multiple replicas would duplicate scheduled work.
- The worker needs outbound access to public RSS feeds and the configured AI provider.
- Job outcomes are written to application logs. This milestone does not yet add a persistent job-history dashboard or notifications.
- No content is automatically approved or published.

## Verification

```bash
docker compose up --build -d
docker compose exec backend pytest -v
docker compose exec backend ruff check --no-cache .
docker compose --profile scheduler up --build -d
docker compose logs --tail=100 research-worker
```
