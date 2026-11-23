from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Liveness check")
async def health_check() -> dict[str, str]:
    """Confirm that the API process is responding."""
    return {"status": "ok"}


@router.get("/health/ready", summary="Readiness check")
async def readiness_check(
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    """Confirm that the API can reach PostgreSQL."""
    await session.execute(text("SELECT 1"))
    return {"status": "ready", "database": "ok"}
