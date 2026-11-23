from collections.abc import AsyncIterator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.db.session import get_db_session
from app.main import app


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
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test",
                ) as test_client:
                    yield test_client
            finally:
                app.dependency_overrides.pop(get_db_session, None)
                await session.close()
                await transaction.rollback()
    finally:
        await test_engine.dispose()
