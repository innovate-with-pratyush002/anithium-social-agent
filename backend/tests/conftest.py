from collections.abc import AsyncIterator
from uuid import uuid4

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import get_db_session
from app.main import app
from app.models.user import User


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    test_engine = create_async_engine(
        get_settings().database_url,
        poolclass=NullPool,
    )
    try:
        async with test_engine.connect() as connection:
            transaction = await connection.begin()
            session = AsyncSession(
                bind=connection,
                expire_on_commit=False,
                join_transaction_mode="create_savepoint",
            )

            async def override_get_db_session() -> AsyncIterator[AsyncSession]:
                yield session

            app.dependency_overrides[get_db_session] = override_get_db_session
            try:
                admin = User(
                    email=f"admin-{uuid4()}@example.com",
                    full_name="Test Admin",
                    password_hash=hash_password("StrongTestPassword123!"),
                    is_active=True,
                    is_admin=True,
                )
                session.add(admin)
                await session.commit()

                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test",
                ) as test_client:
                    login = await test_client.post(
                        "/api/v1/auth/login",
                        json={
                            "email": admin.email,
                            "password": "StrongTestPassword123!",
                        },
                    )
                    assert login.status_code == 200
                    test_client.headers["Authorization"] = (
                        f"Bearer {login.json()['access_token']}"
                    )
                    yield test_client
            finally:
                app.dependency_overrides.pop(get_db_session, None)
                await session.close()
                await transaction.rollback()
    finally:
        await test_engine.dispose()
