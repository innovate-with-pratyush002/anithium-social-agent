# Phase 8 — Research Quality and AI Output Reliability

## Goal

Reduce avoidable analysis failures and make research summaries more conservative about unsupported details, without spending live AI-provider quota during development or tests.

## Changes

- The research-analysis prompt now requires every summary statement and key point to be supported by the supplied title, RSS summary, or stored content.
- It explicitly prohibits filling gaps with model names, versions, capabilities, dates, metrics, quotes, customer outcomes, or other details from memory.
- AI JSON is parsed before Pydantic validation.
- Key points are whitespace-normalized, HTML-cleaned, limited to 300 characters each, deduplicated case-insensitively, and capped at five.
- Invalid JSON, non-object JSON, invalid field types, and other schema violations still fail safely and remain eligible for the existing bounded retry flow.
- Added deterministic tests for excess points, duplicate points, malformed JSON, non-object JSON, and invalid point types.

## API budget

All new tests use local JSON fixtures. They do not initialize an AI provider client or call Groq, OpenAI, or Gemini. No new environment variables or database migration are required.

## Important limitations

- A stricter prompt reduces hallucination risk but does not prove factual correctness. Language models can still produce unsupported claims.
- Truncating excess key points fixes a formatting mismatch; it does not validate the truth of those points.
- The metadata-based quality score remains a heuristic, not a fact-checking system.
- Review source links and important claims before approving content for publication.

## Verification

After pulling the changes:

    docker compose up --build -d
    docker compose exec backend pytest -v
    docker compose exec backend ruff check --no-cache .

No manual AI analysis request is needed to verify this phase.
