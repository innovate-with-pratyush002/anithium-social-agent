# Phase 7 — Milestone 6: Real RSS Source Onboarding

## Goal

Populate the research pipeline with a small, curated set of public RSS/Atom feeds and validate real-world ingestion without enabling automatic publishing.

## Initial source catalog

The seed script adds these eight sources:

| Source | Feed URL | Reliability score |
|---|---|---:|
| OpenAI News | https://openai.com/news/rss.xml | 0.95 |
| Google DeepMind Blog | https://deepmind.google/blog/rss.xml | 0.95 |
| Google Research Blog | https://research.google/blog/rss/ | 0.95 |
| Google AI Blog | https://blog.google/technology/ai/rss/ | 0.95 |
| Hugging Face Blog | https://huggingface.co/blog/feed.xml | 0.90 |
| NVIDIA Blog | https://blogs.nvidia.com/feed/ | 0.90 |
| arXiv Artificial Intelligence | https://rss.arxiv.org/rss/cs.AI | 0.90 |
| arXiv Machine Learning | https://rss.arxiv.org/rss/cs.LG | 0.90 |

The reliability values are initial editorial configuration, not external fact-check scores. Official company feeds are primary sources for what those organizations announce; they are not independent evaluations of their claims. arXiv is a research-preprint repository, so papers still require critical review.

## Seed behavior

Run inside the backend container:

```bash
docker compose exec backend python -m app.scripts.seed_research_sources
```

The operation:
- Requires at least one active administrator account.
- Inserts only catalog URLs that do not already exist.
- Preserves existing source records and administrator edits.
- Assigns the active administrator as the creator.
- Does not fetch feeds, invoke the AI provider, or publish content.

It is safe to run again. Existing catalog entries are skipped.

## Run the first real ingestion

After seeding, trigger ingestion manually through the admin-protected API:

```http
POST /api/v1/research-ingestion/run
Content-Type: application/json

{
  "max_items_per_source": 5
}
```

Or use the existing Swagger UI at `http://localhost:8001/docs`. Authenticate with the admin account first.

Then inspect:
- The ingestion response for source-level failures, fetched entries, created items, and duplicates.
- `GET /api/v1/sources?active=true` to confirm the catalog.
- `GET /api/v1/research-items` to inspect stored articles and quality signals.
- `POST /api/v1/research-intelligence/analyze` to analyze a small batch.
- `GET /api/v1/research-intelligence/ranked` and `/trends` to inspect analyzed research.

## Scheduled validation

Once manual ingestion works, restart the single worker:

```bash
docker compose --profile scheduler restart research-worker
docker compose logs --tail=150 research-worker
```

The worker runs ingestion immediately on startup and then at its configured interval. Keep exactly one worker replica. Ingestion and analysis are separate jobs; newly collected articles may be analyzed by the next analysis run.

## Safety and operational limits

- Feed URLs are subject to the existing HTTP/HTTPS, DNS public-address, no-redirect, response-size, and timeout checks.
- A source failure is isolated and reported; it should not stop other feeds from being processed.
- The initial batch is intentionally small. Review source-level errors before adding more feeds.
- Source reliability scores are manually maintained heuristics and do not establish factual accuracy.
- AI summaries and relevance scores are triage aids, not fact verification.
- No draft is automatically approved or published.

## Verification

```bash
docker compose exec backend pytest -v
docker compose exec backend ruff check --no-cache .
docker compose exec backend python -m app.scripts.seed_research_sources
```
