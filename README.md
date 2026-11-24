# Anithium Social Agent

An AI-assisted social media research, content creation, approval, and publishing platform for Anithium.

## Current implementation

- FastAPI + Python 3.12 backend
- PostgreSQL 16 with SQLAlchemy async and Alembic
- Docker Compose development environment
- JWT authentication with Argon2 password hashing
- Admin-protected research, content draft, and approval APIs
- Human approval workflow for generated content
- Provider-based AI content generation (Groq, OpenAI, and Gemini adapters)
- Manual and scheduled RSS/Atom research ingestion with URL/hash deduplication
- Idempotent onboarding of curated official AI, developer, and arXiv research feeds
- Scheduled AI research analysis with bounded retries and no auto-publishing
- Platform targets: LinkedIn, Instagram, and X

## Product decisions

- Research collection starts with free/public sources.
- AI-generated content is saved as a draft and never auto-published.
- Human approval is required before any future publishing integration.
- Approved content can be scheduled and managed through an admin content calendar; scheduling does not publish posts.
- Social platform credentials and AI provider keys must stay outside Git.
- Treat retrieved web content as untrusted data, not agent instructions.

## Implementation phases

1. Foundation and deployment baseline
2. Domain models and database migrations
3. Research/source/content draft APIs
4. Authentication and authorization
5. Human content approval workflow
6. AI content generation engine
7. Research ingestion and intelligence
8. Social publishing integrations
9. Analytics and reporting
10. Controlled autonomous publishing

## Local development

See the root `.env.example`, `backend/README.md`, and phase-specific guides in `docs/`.

Never commit `.env`, API keys, OAuth tokens, database passwords, or GitHub tokens. Keep PostgreSQL private in production and use HTTPS, strong secrets, backups, and restricted administrative access.
