from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_admin
from app.db.session import get_db_session
from app.schemas.editorial import EditorialOpportunitiesResponse
from app.services.editorial_strategy import get_content_opportunities

router = APIRouter(
    prefix="/editorial",
    tags=["Editorial Strategy"],
    dependencies=[Depends(require_admin)],
)


@router.get("/opportunities", response_model=EditorialOpportunitiesResponse)
async def list_content_opportunities(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    platforms: Annotated[
        list[Literal["linkedin", "instagram", "x"]] | None,
        Query(),
    ] = None,
    window_days: int = Query(default=14, ge=1, le=90),
    limit: int = Query(default=20, ge=1, le=100),
) -> EditorialOpportunitiesResponse:
    return await get_content_opportunities(
        session,
        platforms=platforms or ("linkedin", "instagram", "x"),
        window_days=window_days,
        limit=limit,
    )
