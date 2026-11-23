from uuid import uuid4

from httpx import AsyncClient


async def test_registration_login_and_current_user(client: AsyncClient) -> None:
    email = f"user-{uuid4()}@example.com"
    registration = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Regular User",
            "password": "StrongUserPassword123!",
        },
    )

    assert registration.status_code == 201
    assert registration.json()["email"] == email
    assert registration.json()["is_admin"] is False
    assert "password_hash" not in registration.json()

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": email.upper(), "password": "StrongUserPassword123!"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    assert login.json()["token_type"] == "bearer"
    assert login.json()["expires_in"] > 0

    client.headers["Authorization"] = f"Bearer {token}"
    current_user = await client.get("/api/v1/auth/me")
    assert current_user.status_code == 200
    assert current_user.json()["email"] == email
    assert current_user.json()["is_admin"] is False

    forbidden = await client.post(
        "/api/v1/sources",
        json={
            "name": "Unauthorized Source",
            "source_type": "rss",
            "url": "https://example.com/unauthorized-feed.xml",
        },
    )
    assert forbidden.status_code == 403


async def test_protected_api_rejects_missing_and_invalid_tokens(
    client: AsyncClient,
) -> None:
    original_authorization = client.headers.pop("Authorization")

    missing = await client.get("/api/v1/sources")
    assert missing.status_code == 401

    client.headers["Authorization"] = "Bearer invalid.token.value"
    invalid = await client.get("/api/v1/sources")
    assert invalid.status_code == 401

    client.headers["Authorization"] = original_authorization
