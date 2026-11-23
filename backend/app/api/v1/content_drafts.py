from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.models.content_draft import ContentDraft
from app.schemas.common import PageMeta, PaginatedResponse, validate_pagination
from app.schemas.content_draft import ContentDraftCreate, ContentDraftRead, ContentDraftUpdate

router = APIRouter(prefix="/content-drafts", tags=["Content Drafts"])

@router.post("", response_model=ContentDraftRead, status_code=status.HTTP_201_CREATED)
async def create_content_draft(
    payload: ContentDraftCreate, session: AsyncSession = Depends(get_db_session)
):
    draft = ContentDraft(**payload.model_dump(mode="json"))
    session.add(draft)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail="The linked research item does not exist.") from exc
    await session.refresh(draft)
    return draft

@router.get("", response_model=PaginatedResponse[ContentDraftRead])
async def list_content_drafts(
    platform: str | None = Query(default=None, max_length=20),
    draft_status: str | None = Query(default=None, alias="status", max_length=24),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db_session),
):
    limit, offset = validate_pagination(limit, offset)
    filters = []
    if platform:
        filters.append(ContentDraft.platform == platform)
    if draft_status:
        filters.append(ContentDraft.status == draft_status)
    total = await session.scalar(select(func.count()).select_from(ContentDraft).where(*filters))
    result = await session.scalars(
        select(ContentDraft).where(*filters).order_by(ContentDraft.created_at.desc())
        .limit(limit).offset(offset)
    )
    return {"items": result.all(), "pagination": PageMeta(total=total or 0, limit=limit, offset=offset)}

@router.get("/{draft_id}", response_model=ContentDraftRead)
async def get_content_draft(draft_id: str, session: AsyncSession = Depends(get_db_session)):
    draft = await session.get(ContentDraft, draft_id)
    if draft is None:
        raise HTTPException(status_code=404, detail="Content draft not found.")
    return draft

@router.patch("/{draft_id}", response_model=ContentDraftRead)
async def update_content_draft(
    draft_id: str, payload: ContentDraftUpdate, session: AsyncSession = Depends(get_db_session)
):
    draft = await session.get(ContentDraft, draft_id)
    if draft is None:
        raise HTTPException(status_code=404, detail="Content draft not found.")
    for key, value in payload.model_dump(exclude_unset=True, mode="json").items():
        setattr(draft, key, value)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail="The linked research item does not exist.") from exc
    await session.refresh(draft)
    return draft

@router.delete("/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content_draft(draft_id: str, session: AsyncSession = Depends(get_db_session)):
    draft = await session.get(ContentDraft, draft_id)
    if draft is None:
        raise HTTPException(status_code=404, detail="Content draft not found.")
    await session.delete(draft)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=409,
            detail="This draft has publishing history and cannot be deleted.",
        ) from exc
