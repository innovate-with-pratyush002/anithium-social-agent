# Phase 3 — Backend API Foundation

## Delivered

- Versioned API prefix: `/api/v1`
- Sources endpoints for create, list/filter, retrieve, patch, and soft-deactivate.
- Research item endpoints for create, list/filter, retrieve, and patch.
- Content draft endpoints for create, list/filter, retrieve, patch, and delete.
- Pydantic v2 request/response schemas with UUID, URL, enum, length, and numeric validation.
- Shared paginated response envelope with a maximum page size of 100.
- Database sessions injected through FastAPI dependencies.
- Duplicate and relational integrity conflicts translated into HTTP 409 responses.
- OpenAPI documentation available at `/docs`.

## Endpoint summary

| Resource | Method | Path | Purpose |
|---|---|---|---|
| Sources | POST | `/api/v1/sources` | Create a source |
| Sources | GET | `/api/v1/sources` | List sources; optional `active`, `limit`, `offset` |
| Sources | GET | `/api/v1/sources/{source_id}` | Retrieve a source |
| Sources | PATCH | `/api/v1/sources/{source_id}` | Update source fields |
| Sources | DELETE | `/api/v1/sources/{source_id}` | Soft-deactivate a source |
| Research | POST | `/api/v1/research-items` | Create a research item |
| Research | GET | `/api/v1/research-items` | List; optional `status`, `topic`, `source_id`, pagination |
| Research | GET | `/api/v1/research-items/{item_id}` | Retrieve a research item |
| Research | PATCH | `/api/v1/research-items/{item_id}` | Update research fields |
| Drafts | POST | `/api/v1/content-drafts` | Create a draft |
| Drafts | GET | `/api/v1/content-drafts` | List; optional `platform`, `status`, pagination |
| Drafts | GET | `/api/v1/content-drafts/{draft_id}` | Retrieve a draft |
| Drafts | PATCH | `/api/v1/content-drafts/{draft_id}` | Update a draft |
| Drafts | DELETE | `/api/v1/content-drafts/{draft_id}` | Delete a draft unless publishing history restricts it |

## Response pagination

List endpoints return:

```json
{
  "items": [],
  "pagination": {
    "total": 0,
    "limit": 20,
    "offset": 0
  }
}
```

## Important security note

Authentication and authorization are not implemented in this phase. These endpoints must remain behind a trusted development environment or network boundary until the authentication and authorization phase is complete. Do not expose this API publicly yet.

## Verification

Run:

```bash
docker compose up --build -d
docker compose exec backend pytest -v
docker compose exec backend ruff check .
``

Then open `http://localhost:8001/docs` (adjust the host port if your local Compose mapping differs).
