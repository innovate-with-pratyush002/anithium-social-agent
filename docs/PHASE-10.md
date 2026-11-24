# Phase 10 — Content Calendar and Scheduling Workflow

## Goal

Allow an administrator to schedule human-approved content drafts for a future date and review or cancel queued schedule records. This phase records scheduling intent only; it does not publish to LinkedIn, Instagram, or X.

## Endpoints

All endpoints require an administrator bearer token.

- `POST /api/v1/publishing/schedules`: schedule an approved draft.
- `GET /api/v1/publishing/schedules`: list schedule records.
- `DELETE /api/v1/publishing/schedules/{schedule_id}`: cancel a queued schedule.

The create request requires `content_draft_id` and a future `scheduled_at` timestamp with an explicit timezone. Timestamps are normalized to UTC.

The list endpoint supports `status`, `platform`, `from_at`, `to_at`, `limit`, and `offset`.

## Workflow and safeguards

- Only drafts with status `approved` can be scheduled.
- Scheduling creates a `publishing_records` row with status `queued` and changes the draft status to `scheduled`.
- A draft cannot receive another queued, publishing, or published record.
- Only queued records can be cancelled.
- Cancellation changes the record to `cancelled` and restores the draft to `approved`.
- This phase does not call social APIs, does not publish due records, and does not bypass human approval.
- No new credentials, environment variables, or database migrations are required; the publishing record model and table already exist.

## Verification

```bash
docker compose --profile scheduler up --build -d
docker compose exec backend pytest -v
docker compose exec backend ruff check --no-cache .
```
