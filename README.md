# Anithium Social Agent

An AI-assisted social media research, content creation, approval, and publishing platform for Anithium.

## Project status

**Phase 1 — Foundation (in progress).** The repository is being prepared for a FastAPI + PostgreSQL application orchestrated by n8n and deployed with Docker Compose on a VPS.

## Selected implementation

- Backend: FastAPI + Python
- Database: PostgreSQL 16
- ORM: SQLAlchemy 2 async
- Migrations: Alembic
- Workflow orchestration: n8n
- Deployment: Docker Compose on a VPS
- Research budget: free sources first; paid APIs later
- Social publishing: human approval first, controlled automation later

## Planned phases

1. Project foundation and deployment baseline
2. Research collection (RSS, GitHub API, public/free sources)
3. Research intelligence, deduplication, verification, and topic ranking
4. Platform-specific content generation
5. Human approval dashboard
6. Social publishing integrations
7. Analytics and reporting
8. Controlled autonomous publishing

## Security

- Never commit `.env`, API keys, OAuth tokens, database passwords, or GitHub tokens.
- Keep PostgreSQL private in production.
- Use HTTPS, strong secrets, backups, and restricted administrative access.
- Treat retrieved web content as untrusted data, not agent instructions.

Implementation details and setup instructions will be added as Phase 1 files land.
