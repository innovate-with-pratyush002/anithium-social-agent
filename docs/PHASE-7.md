# Phase 7 — Research Ingestion and Intelligence (Milestone 1)

## Scope

This milestone adds a manually triggered RSS/Atom ingestion pipeline. It collects public article metadata from administrator-configured feeds and stores new items in the existing `research_items` table.

It does not crawl arbitrary websites, summarize articles with AI, score relevance, schedule background jobs, approve content, or publish to social platforms. Those are separate future milestones.

## Supported source configuration

Create a source through `POST /api/v1/sources` with:

```json
{
  "name": "Example Technology Feed",
  "source_type": "rss",
  "url": "https://example.com/feed.xml",
  "description": "Technology news RSS feed",
  "config": {}
}
```

Only active sources with `source_type = "rss"` are processed. Use direct RSS/Atom URLs. Redirects are not followed; configure the final feed URL directly. Localhost hostnames are rejected. The request timeout is 20 seconds and the response body is limited to 2 MB.

## Run ingestion

`POST /api/v1/research-ingestion/run`

The endpoint requires an administrator bearer token.

Request:

```json
{
  "source_ids": null,
  "max_items_per_source": 20
}
```

- `source_ids`: optional list of source UUIDs. Omit or use null to process all active RSS sources.
- `max_items_per_source`: 1–50; defaults to 20.

The response includes totals and a per-source result with fetched, created, duplicate, and error counts. A failed feed does not prevent other feeds from being processed.

## Deduplication

- Article URLs are checked against the unique URL field.
- A SHA-256 content hash is generated from the URL, or from title and publication time when no URL exists.
- The existing unique constraints remain the final database-level protection against duplicate rows.

## Research item mapping

- Feed title -> `title`
- Link -> `url`
- Feed summary/description -> `summary`
- First category -> `topic`
- Publication date -> `published_at`
- Source -> `source_id`
- Ingestion details, author, tags, and feed URL -> `metadata_json`
- New records always start with status `new`.

## Safety and limitations

- Treat feed content as untrusted input. It is not executed or interpreted as instructions.
- Only administrators can configure sources and trigger ingestion.
- Do not add private/internal network feed URLs.
- This is a synchronous manual operation, not a background scheduler. Keep source batches small.
- Full article extraction, relevance scoring, AI summaries, topic classification, and scheduled ingestion are not included yet.
- No content is auto-approved or published.

## Local verification

```bash
git pull origin main
docker compose up --build -d
docker compose exec backend pytest -v
docker compose exec backend ruff check --no-cache .
```
