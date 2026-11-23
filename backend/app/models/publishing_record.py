import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.content_draft import ContentDraft


class PublishingRecord(TimestampMixin, Base):
    __tablename__ = "publishing_records"
    __table_args__ = (
        CheckConstraint(
            "platform IN ('linkedin', 'instagram', 'x')", name="ck_publishing_records_platform"
        ),
        CheckConstraint(
            "status IN ('queued', 'publishing', 'published', 'failed', 'cancelled')",
            name="ck_publishing_records_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    content_draft_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("content_drafts.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    platform: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="queued", nullable=False)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    external_post_id: Mapped[str | None] = mapped_column(String(255))
    external_url: Mapped[str | None] = mapped_column(String(2048))
    error_message: Mapped[str | None] = mapped_column(Text)

    content_draft: Mapped["ContentDraft"] = relationship(back_populates="publishing_records")
