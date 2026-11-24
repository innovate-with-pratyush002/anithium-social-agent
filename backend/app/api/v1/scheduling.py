from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_admin
from app.db.session import get_db_session
from app.models.content_draft import ContentDraft
from app.models.publishing_record import PublishingRecord
from app.schemas.common import PageMeta
from app.schemas.scheduling import ScheduleCreate, ScheduleListResponse, ScheduleRead

router = APIRouter(
    prefix="/publishing",
    tags=["Content Calendar"],
    dependencies=[Depends(require_admin)],
)


@router.post(
    "/schedules",
    response_model=ScheduleRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_schedule(
    payload: ScheduleCreate,
    session: AsyncSession = Depends(get_db_session),
) -> PublishingRecord:
    draft = await session.scalar(
        select(ContentDraft)
        .where(ContentDraft.id == payload.content_draft_id)
        .with_for_update()
    )
    if draft is None:
        raise HTTPException(status_code=404, detail="Content draft not found.")
    if draft.status != "approved":
        raise HTTPException(
            status_code=409,
            detail="Only human-approved drafts can be scheduled.",
        )

    existing = await session.scalar(
        select(PublishingRecord.id).where(
            PublishingRecord.content_draft_id == draft.id,
            PublishingRecord.status.in_(["queued", "publishing", "published"]),
        )
    )
    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="This draft already has an active or completed publishing record.",
        )

    record = PublishingRecord(
        content_draft_id=draft.id,
        platform=draft.platform,
        status="queued",
        scheduled_at=payload.scheduled_at,
    )
    draft.status = "scheduled"
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


@router.get("/schedules", response_model=ScheduleListResponse)
async def list_schedules(
    schedule_status: str | None = Query(default=None, alias="status", max_length=24),
    platform: str | None = Query(default=None, max_length=20),
    from_at: datetime | None = Query(default=None),
    to_at: datetime | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db_session),
) -> ScheduleListResponse:
    filters = []
    if schedule_status:
        filters.append(PublishingRecord.status == schedule_status)
    if platform:
        filters.append(PublishingRecord.platform == platform)
    if from_at:
        if from_at.tzinfo is None or from_at.utcoffset() is None:
            raise HTTPException(status_code=422, detail="from_at must include a timezone.")
        filters.append(PublishingRecord.scheduled_at >= from_at.astimezone(UTC))
    if to_at:
        if to_at.tzinfo is None or to_at.utcoffset() is None:
            raise HTTPException(status_code=422, detail="to_at must include a timezone.")
        filters.append(PublishingRecord.scheduled_at <= to_at.astimezone(UTC))
    if from_at and to_at and from_at > to_at:
        raise HTTPException(status_code=422, detail="from_at must be earlier than to_at.")

    total = await session.scalar(
        select(func.count()).select_from(PublishingRecord).where(*filters)
    )
    result = await session.scalars(
        select(PublishingRecord)
        .where(*filters)
        .order_by(PublishingRecord.scheduled_at.asc().nullslast())
        .limit(limit)
        .offset(offset)
    )
    return ScheduleListResponse(
        items=list(result.all()),
        pagination=PageMeta(total=total or 0, limit=limit, offset=offset),
    )


@router.delete("/schedules/{schedule_id}", response_model=ScheduleRead)
async def cancel_schedule(
    schedule_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> PublishingRecord:
    record = await session.scalar(
        select(PublishingRecord)
        .where(PublishingRecord.id == schedule_id)
        .with_for_update()
    )
    if record is None:
        raise HTTPException(status_code=404, detail="Schedule not found.")
    if record.status != "queued":
        raise HTTPException(
            status_code=409,
            detail="Only queued schedules can be cancelled.",
        )

    record.status = "cancelled"
    draft = await session.get(ContentDraft, record.content_draft_id)
    if draft is not None and draft.status == "scheduled":
        draft.status = "approved"
    await session.commit()
    await session.refresh(record)
    return record
