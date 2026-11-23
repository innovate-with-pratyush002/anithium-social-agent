# Phase 4 — Authentication and Authorization

## Implemented

- Public account registration: `POST /api/v1/auth/register`
- JSON email/password login: `POST /api/v1/auth/login`
- Current account: `GET /api/v1/auth/me`
- Passwords are hashed with Argon2id using `argon2-cffi`; plaintext passwords are never stored or returned.
- Login issues a signed HS256 JWT access token.
- Access-token lifetime is configurable with `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 1440 minutes; allowed: 5–10080).
- Protected APIs require `Authorization: Bearer <access_token>`.
- All source, research-item, and content-draft endpoints require an active authenticated user.
- Mutating those resources requires an administrator.
- Newly registered users always receive `is_admin = false`; the public registration payload cannot set roles.
- Source creation records the authenticated administrator as `created_by_id`.

## First administrator bootstrap

Public registration deliberately never grants administrator privileges. After registering the account that should own the installation, promote it manually from the trusted server:

```bash
docker compose exec postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

Then, inside psql, run this query with the exact registered email:

```sql
UPDATE users
SET is_admin = TRUE
WHERE email = 'your-admin-email@example.com';
```

Verify exactly one row was updated. Exit psql with `\\q`, then log in again to obtain a fresh token. Do not expose database credentials or run this promotion through a public API.

## API usage

Register:

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "admin@example.com",
  "full_name": "Anithium Admin",
  "password": "use-a-unique-password-at-least-12-chars"
}
```

Login:

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "admin@example.com",
  "password": "your-password"
}
```

Use the returned token:

```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

## Security notes and current limitations

- Keep `SECRET_KEY` private and use a cryptographically random value of at least 32 characters in production.
- Serve the API only over HTTPS outside local development.
- Tokens are stateless access tokens. Logout/revocation and refresh-token rotation are not implemented in this phase; a token remains valid until expiry unless its user is deactivated.
- Rate limiting, email verification, password reset, audit events for authentication, and account lockout are future hardening tasks.
- Do not expose the backend publicly until production secrets, HTTPS, rate limiting, and the initial administrator bootstrap are configured.
