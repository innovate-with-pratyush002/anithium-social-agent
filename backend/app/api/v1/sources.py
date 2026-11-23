from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.models.source import Source
from app.schemas.common import PageMeta, PaginatedResponse
from app.schemas.source import SourceCreate, SourceRead, SourceUpdate

router = APIRouter(prefix="/sources", tags=["Sources"])

@router.post("", response_model=SourceRead, status_code=status.HTTP_201_CREATED)
async def create_source(payload: SourceCreate, session: AsyncSession = Depends(get_db_session)):
    data = payload.model_dump()
    data["url"] = str(payload.url)
    source = Source(**data)
    session.add(source)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail="A source with this URL already exists.") from exc
    await session.refresh(source)
    return source

@router.get("", response_model=PaginatedResponse[SourceRead])
async def list_sources(
    active: bool | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db_session),
):
    filters = [Source.is_active == active] if active is not None else []
    total = await session.scalar(select(func.count()).select_from(Source).where(*filters))
    result = await session.scalars(
        select(Source).where(*filters).order_by(Source.created_at.desc()).limit(limit).offset(offset)
    )
    return {"items": result.all(), "pagination": PageMeta(total=total or 0, limit=limit, offset=offset)}

@router.get("/{source_id}", response_model=SourceRead)
async def get_source(source_id: UUID, session: AsyncSession = Depends(get_db_session)):
    source = await session.get(Source, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found.")
    return source

@router.patch("/{source_id}", response_model=SourceRead)
async def update_source(
    source_id: UUID, payload: SourceUpdate, session: AsyncSession = Depends(get_db_session)
):
    source = await session.get(Source, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found.")
    changes = payload.model_dump(exclude_unset=True)
    if changes.get("url") is not None:
        changes["url"] = str(changes["url"])
    for key, value in changes.items():
        setattr(source, key, value)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail="A source with this URL already exists.") from exc
    await session.refresh(source)
    return source

@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_source(source_id: UUID, session: AsyncSession = Depends(get_db_session)):
    source = await session.get(Source, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found.")
    source.is_active = False
    await session.commit()
