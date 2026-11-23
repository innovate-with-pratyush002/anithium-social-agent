# Backend

FastAPI service for Anithium Social Agent.

## Local setup

Requires Python 3.12+ and PostgreSQL 16.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Set environment variables from the repository root `.env.example`. When running Python outside Docker, set the database hostname in `DATABASE_URL` to `localhost`.

```bash
alembic upgrade head
uvicorn app.main:app --reload
pytest
ruff check .
```
