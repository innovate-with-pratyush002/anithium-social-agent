# Phase 6 — AI Content Generation Engine

## Overview

The content generation API converts one stored research item into one draft per requested social platform. The initial provider is OpenAI Chat Completions, isolated behind a provider protocol so another provider can be added without changing the API contract.

## Configuration

Set these variables in the root `.env` file:

```dotenv
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4o-mini
```

The API key is optional at application startup. The generation endpoint returns HTTP 503 until a key is configured. Never commit the real key or paste it into chat.

## Endpoint

`POST /api/v1/content-generation/generate`

Example request:

```json
{
  "research_item_id": "existing-research-item-uuid",
  "platforms": ["linkedin", "instagram", "x"],
  "language": "en",
  "tone": "informative, confident, and conversational",
  "target_audience": "technology professionals and founders",
  "call_to_action": "What is your experience?"
}
```

The endpoint:
- Requires administrator authentication.
- Validates the research item exists.
- Generates platform-specific content.
- Saves all generated drafts only after all requested platform generations succeed.
- Always creates drafts with status `draft`; it never approves or publishes content.
- Stores provider, model, and source research ID in generation metadata.
- Returns 502 for provider or output errors without saving a partial set.

## Safety and limitations

- Retrieved research text is treated as untrusted source material, not instructions.
- The model is instructed not to invent facts, statistics, or quotations.
- Model output still requires human fact-checking and approval.
- Each requested platform currently makes a separate provider request.
- OpenAI usage may incur charges according to the selected model and account pricing.
- The endpoint does not publish to any social platform.

## Verification

```bash
docker compose up --build -d
docker compose exec backend pytest -v
docker compose exec backend ruff check --no-cache .
```

Tests use a fake provider and do not make paid network calls.
