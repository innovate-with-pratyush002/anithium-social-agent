# Phase 11.1 — Social Account Security Foundation

## Scope

This milestone prepares secure storage and account lifecycle management for LinkedIn, Instagram, and X integrations. It does not yet perform OAuth authorization or publish posts.

## Implemented

- A SocialAccount database model tied to the authenticated admin user.
- Encrypted access-token and refresh-token storage fields.
- Fernet-based token encryption/decryption helpers.
- A required encryption key setting, kept outside Git.
- Admin endpoints to list connected accounts and disconnect an account.
- Disconnecting deactivates the account and clears stored token material.
- API response schemas never expose encrypted tokens.

## Configuration

Generate a Fernet key:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Add the generated value to the local .env as SOCIAL_TOKEN_ENCRYPTION_KEY. Do not commit it or send it in chat. Back it up securely; losing it makes stored tokens undecryptable.

## Endpoints

- GET /api/v1/social-accounts
- DELETE /api/v1/social-accounts/{account_id}

Both endpoints require admin authentication.

## Migration

Run:

```bash
docker compose exec backend alembic upgrade head
```

## Not included yet

- OAuth start/callback/state/PKCE flows.
- Platform-specific token exchange and refresh.
- Live publishing adapters or publishing worker.
- Media upload workflows.

These are deliberately deferred until app credentials, redirect URLs, account types, and required platform permissions are confirmed.
