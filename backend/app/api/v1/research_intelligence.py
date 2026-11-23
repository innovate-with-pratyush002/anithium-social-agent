from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_admin
from app.db.session import get_db_session
from app.models.research_item import ResearchItem
from app.schemas.common import PageMeta, PaginatedResponse
from app.schemas.research_intelligence import (
    ResearchIntelligenceRequest,
    ResearchIntelligenceResponse,
)
from app.schemas.research_item import ResearchItemRead
from app.services.research_intelligence import (
    ResearchAnalyzer,
    analyze_pending_research,
    get_research_analyzer,
)

router = APIRouter(
    prefix="/research-intelligence",
    tags=["Research Intelligence"],
    dependencies=[Depends(require_admin)],
)


@router.post("/analyze", response_model=ResearchIntelligenceResponse)
async def analyze_research(
    payload: ResearchIntelligenceRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    analyzer: Annotated[ResearchAnalyzer, Depends(get_research_analyzer)],
) -> ResearchIntelligenceResponse:
    return await analyze_pending_research(session, payload, analyzer)


@router.get("/ranked", response_model=PaginatedResponse[ResearchItemRead])
async def list_ranked_research(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: Annotated[AsyncSession, Depends(get_db_session)] = None,
):
    filters = [ResearchItem.relevance_score.is_not(None)]
    total = await session.scalar(
        select(func.count()).select_from(ResearchItem).where(*filters)
    )
    items = await session.scalars(
        select(ResearchItem)
        .where(*filters)
        .order_by(ResearchItem.relevance_score.desc(), ResearchItem.discovered_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return {
        "items": items.all(),
        "pagination": PageMeta(total=total or 0, limit=limit, offset=offset),
    }
