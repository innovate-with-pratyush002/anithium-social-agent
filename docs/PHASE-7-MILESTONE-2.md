# Phase 7 — Milestone 2: Research Intelligence

## Scope

This milestone analyzes stored research metadata with the configured AI provider. It does not fetch arbitrary article pages, crawl websites, schedule jobs, approve content, or publish posts.

## Analyze pending research

POST /api/v1/research-intelligence/analyze

Requires an administrator bearer token.

Request:

    {
      "max_items": 10
    }

The endpoint processes up to 20 items per request. It selects items with status new and no relevance score. Optionally pass research_item_ids (up to 20 UUIDs) to analyze only a selected set; an empty list selects no items. Each item is analyzed independently; a failed item does not stop the remaining batch.

The AI returns:
- A concise summary based only on supplied title, feed summary/content and topic.
- A topic label.
- A language code.
- A relevance score from 0.0 to 1.0 for Anithium's technology, AI, software and developer audience.
- Up to five key points.

The summary, topic, language and score are stored on the research item. Provider, model, analysis timestamp and key points are stored under metadata_json.intelligence. Analyzed items retain their existing workflow status; the non-null relevance score prevents accidental repeat processing.

## Ranked research

GET /api/v1/research-intelligence/ranked?limit=20&offset=0

Returns analyzed research ordered by relevance score descending, then discovery time.

## Provider configuration

Uses the existing AI_PROVIDER and provider-specific API key/model settings. No automatic provider fallback is performed. AI source text is treated as untrusted data. Article URLs are stored as references but are not fetched by this milestone.

## Verification

    git pull origin main
    docker compose up --build -d
    docker compose exec backend pytest -v
    docker compose exec backend ruff check --no-cache .
