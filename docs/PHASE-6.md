# Phase 6 — AI Content Generation Engine

## Overview

The content generation API converts one stored research item into one draft per requested social platform. The API uses a provider-neutral content generator and an OpenAI-compatible adapter. Groq is the default provider; OpenAI and Google Gemini can be selected through environment variables without changing Python code.

## Provider configuration

Set the active provider in the root `.env` file:

```dotenv
AI_PROVIDER=groq

GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=openai/gpt-oss-20b

OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini

GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
```

Only the selected provider's API key is required. The other provider keys can remain empty.

To switch providers, change `AI_PROVIDER`, set that provider's key, and select its model:

- Groq: `AI_PROVIDER=groq`, `GROQ_API_KEY`, `GROQ_MODEL`
- OpenAI: `AI_PROVIDER=openai`, `OPENAI_API_KEY`, `OPENAI_MODEL`
- Gemini: `AI_PROVIDER=gemini`, `GEMINI_API_KEY`, `GEMINI_MODEL`

The adapter uses these OpenAI-compatible endpoints:
- Groq: `https://api.groq.com/openai/v1`
- OpenAI: official SDK default endpoint
- Gemini: `https://generativelanguage.googleapis.com/v1beta/openai/`

Groq and Gemini document compatibility with the OpenAI client interface. Provider/model availability and supported parameters can change; use model IDs currently available in the provider's account and documentation.

The application does not automatically fall back to another provider. This is intentional: a missing key or provider failure is reported instead of silently switching to a potentially billable provider.

API keys are optional at application startup. The generation endpoint returns HTTP 503 if the selected provider's key is missing. Never commit real keys or paste them into chat.

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
- Stores selected provider, model, and source research ID in generation metadata.
- Returns 502 for provider or output errors without saving a partial set.

## Safety and limitations

- Retrieved research text is treated as untrusted source material, not instructions.
- The model is instructed not to invent facts, statistics, or quotations.
- Model output still requires human fact-checking and approval.
- Each requested platform currently makes a separate provider request.
- Free tiers have provider-specific quotas and rate limits; they are not unlimited. Check the provider's current pricing and limits before use.
- The endpoint does not publish to any social platform.

## Verification

```bash
docker compose up --build -d
docker compose exec backend pytest -v
docker compose exec backend ruff check --no-cache .
```

Tests use a fake provider and do not make paid network calls.
