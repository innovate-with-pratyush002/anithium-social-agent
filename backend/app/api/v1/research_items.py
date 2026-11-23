from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.models.research_item import ResearchItem
from app.schemas.common import PageMeta, PaginatedResponse
from app.schemas.research_item import ResearchItemCreate, ResearchItemRead, ResearchItemUpdate

router = APIRouter(prefix="/research-items", tags=["Research Items"])

@router.post("", response_model=ResearchItemRead, status_code=status.HTTP_201_CREATED)
async def create_research_item(
    payload: ResearchItemCreate, session: AsyncSession = Depends(get_db_session)
):
    item = ResearchItem(**payload.model_dump(mode="json"))
    session.add(item)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=409, detail="The source, URL, or content hash conflicts with an existing record."
        ) from exc
    await session.refresh(item)
    return item

@router.get("", response_model=PaginatedResponse[ResearchItemRead])
async def list_research_items(
    item_status: str | None = Query(default=None, alias="status", max_length=24),
    topic: str | None = Query(default=None, max_length=120),
    source_id: UUID | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db_session),
):
    filters = []
    if item_status:
        filters.append(ResearchItem.status == item_status)
    if topic:
        filters.append(ResearchItem.topic == topic)
    if source_id:
        filters.append(ResearchItem.source_id == source_id)
    total = await session.scalar(select(func.count()).select_from(ResearchItem).where(*filters))
    result = await session.scalars(
        select(ResearchItem).where(*filters).order_by(ResearchItem.discovered_at.desc())
        .limit(limit).offset(offset)
    )
    return {"items": result.all(), "pagination": PageMeta(total=total or 0, limit=limit, offset=offset)}

@router.get("/{item_id}", response_model=ResearchItemRead)
async def get_research_item(item_id: UUID, session: AsyncSession = Depends(get_db_session)):
    item = await session.get(ResearchItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Research item not found.")
    return item

@router.patch("/{item_id}", response_model=ResearchItemRead)
async def update_research_item(
    item_id: UUID, payload: ResearchItemUpdate, session: AsyncSession = Depends(get_db_session)
):
    item = await session.get(ResearchItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Research item not found.")
    for key, value in payload.model_dump(exclude_unset=True, mode="json").items():
        setattr(item, key, value)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=409, detail="The source, URL, or content hash conflicts with an existing record."
        ) from exc
    await session.refresh(item)
    return item
