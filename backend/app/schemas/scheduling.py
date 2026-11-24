from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import PageMeta

Platform = str


class ScheduleCreate(BaseModel):
    content_draft_id: UUID
    scheduled_at: datetime

    @field_validator("scheduled_at")
    @classmethod
    def require_timezone_and_future(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("scheduled_at must include a timezone.")
        if value <= datetime.now(UTC):
            raise ValueError("scheduled_at must be in the future.")
        return value.astimezone(UTC)


class ScheduleRead(BaseModel):
    id: UUID
    content_draft_id: UUID
    platform: str
    status: str
    scheduled_at: datetime | None
    published_at: datetime | None
    external_post_id: str | None
    external_url: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime


class ScheduleListResponse(BaseModel):
    items: list[ScheduleRead]
    pagination: PageMeta
