# Phase 1 — Project Foundation

## Included

- FastAPI application and liveness/readiness endpoints
- Pydantic Settings configuration
- Async SQLAlchemy engine and session dependency
- Alembic async migration environment
- PostgreSQL 16 service
- Docker Compose baseline
- Basic API tests
- Secret-safe environment template

## Start with Docker

```bash
cp .env.example .env
# Edit .env: set POSTGRES_PASSWORD and SECRET_KEY.
docker compose up --build -d
docker compose exec backend alembic upgrade head
```

Open `http://localhost:8000/health`, `http://localhost:8000/health/ready`, and `http://localhost:8000/docs`.

## Notes

- Inside Compose, the database hostname is `postgres`; use `localhost` for host-run Python.
- Compose publishes API and database ports on loopback only. Put an HTTPS reverse proxy in front for VPS access.
- The backend container runs as a non-root user.
- Replace example secrets before running.
- n8n will be added in a later step with its own persistent storage and encryption configuration.
- This scaffold has not yet been runtime-tested on the user's machine or VPS.
