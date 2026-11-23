# Phase 2 — Core Database Domain

## Included

- UUID primary keys across domain entities
- Shared timezone-aware created/updated timestamps
- User records with admin/active flags (authentication is a later phase)
- Configurable research sources
- Deduplicatable research items with canonical URL and content hash uniqueness
- Platform-specific content drafts for LinkedIn, Instagram, and X
- One-to-one manual approval record per content draft
- Publishing history and scheduling metadata
- Foreign keys, deletion behavior, indexes, and check constraints
- Alembic metadata registration for migration autogeneration

## Domain flow

`Source -> ResearchItem -> ContentDraft -> Approval -> PublishingRecord`

A research item can produce multiple platform drafts. Each draft can have one approval record and multiple publishing attempts/records. Publishing is not triggered by these models; actual publishing integration will be implemented in a later phase.

## Apply the initial schema locally

After pulling the latest `main` branch:

```bash
docker compose up --build -d
docker compose exec backend alembic revision --autogenerate -m "create core domain tables"
```

Review the generated migration under `backend/migrations/versions/`. Confirm that it creates all six tables and the expected foreign keys, indexes, unique constraints, and check constraints. Then apply it:

```bash
docker compose exec backend alembic upgrade head
docker compose exec backend pytest -v
```

Inspect the current revision:

```bash
docker compose exec backend alembic current
```

## Design notes

- Statuses and platform identifiers are stored as constrained strings for straightforward API serialization.
- JSON columns hold source configuration, hashtags, media URLs, and generation metadata; relational fields remain normal columns.
- No credentials, OAuth tokens, or social platform secrets are stored in these domain tables.
- The user table is a domain foundation, not a complete authentication implementation.
- All generated posts remain drafts until an explicit approval workflow is implemented.
