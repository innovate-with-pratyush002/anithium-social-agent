from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies import require_admin
from app.db.session import get_db_session
from app.models.approval import Approval
from app.models.content_draft import ContentDraft
from app.models.user import User
from app.schemas.approval import ApprovalDecisionRequest, ApprovalRead, ApprovalStatus
from app.schemas.common import PageMeta, PaginatedResponse

router = APIRouter(
    prefix="/approvals",
    tags=["Approvals"],
    dependencies=[Depends(require_admin)],
)


async def _load_approval(session: AsyncSession, approval_id: UUID) -> Approval:
    result = await session.scalars(
        select(Approval)
        .options(selectinload(Approval.content_draft))
        .where(Approval.id == approval_id)
    )
    approval = result.one_or_none()
    if approval is None:
        raise HTTPException(status_code=404, detail="Approval not found.")
    return approval


@router.post(
    "/content-drafts/{draft_id}/submit-for-approval",
    response_model=ApprovalRead,
    status_code=status.HTTP_201_CREATED,
)
async def submit_draft_for_approval(
    draft_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    draft = await session.get(ContentDraft, draft_id)
    if draft is None:
        raise HTTPException(status_code=404, detail="Content draft not found.")
    if draft.status != "draft":
        raise HTTPException(
            status_code=409,
            detail="Only drafts in draft status can be submitted for approval.",
        )

    result = await session.scalars(
        select(Approval).where(Approval.content_draft_id == draft_id)
    )
    approval = result.one_or_none()
    if approval is not None:
        if approval.status == "pending":
            raise HTTPException(status_code=409, detail="This draft is already awaiting approval.")
        if approval.status == "approved":
            raise HTTPException(status_code=409, detail="This draft has already been approved.")
        approval.status = "pending"
        approval.feedback = None
        approval.reviewer_id = None
        approval.reviewed_at = None
    else:
        approval = Approval(content_draft_id=draft_id, status="pending")
        session.add(approval)

    draft.status = "pending_approval"
    await session.flush()
    approval_id = approval.id
    await session.commit()
    return await _load_approval(session, approval_id)


@router.get("", response_model=PaginatedResponse[ApprovalRead])
async def list_approvals(
    approval_status: ApprovalStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db_session),
):
    filters = [Approval.status == approval_status] if approval_status else []
    total = await session.scalar(select(func.count()).select_from(Approval).where(*filters))
    result = await session.scalars(
        select(Approval)
        .options(selectinload(Approval.content_draft))
        .where(*filters)
        .order_by(Approval.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return {
        "items": result.all(),
        "pagination": PageMeta(total=total or 0, limit=limit, offset=offset),
    }


@router.get("/{approval_id}", response_model=ApprovalRead)
async def get_approval(
    approval_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    return await _load_approval(session, approval_id)


@router.post("/{approval_id}/decision", response_model=ApprovalRead)
async def decide_approval(
    approval_id: UUID,
    payload: ApprovalDecisionRequest,
    reviewer: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db_session),
):
    approval = await _load_approval(session, approval_id)
    if approval.status != "pending":
        raise HTTPException(
            status_code=409,
            detail="A decision can only be recorded for a pending approval.",
        )

    approval.status = payload.decision
    approval.feedback = payload.feedback.strip() if payload.feedback else None
    approval.reviewer_id = reviewer.id
    approval.reviewed_at = datetime.now(UTC)
    approval.content_draft.status = "approved" if payload.decision == "approved" else "draft"

    await session.commit()
    return await _load_approval(session, approval_id)
