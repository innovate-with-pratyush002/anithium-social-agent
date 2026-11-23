import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, CheckConstraint, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.approval import Approval
    from app.models.publishing_record import PublishingRecord
    from app.models.research_item import ResearchItem


class ContentDraft(TimestampMixin, Base):
    __tablename__ = "content_drafts"
    __table_args__ = (
        CheckConstraint(
            "platform IN ('linkedin', 'instagram', 'x')", name="ck_content_drafts_platform"
        ),
        CheckConstraint(
            "status IN ('draft', 'pending_approval', 'approved', 'scheduled', "
            "'published', 'failed', 'archived')",
            name="ck_content_drafts_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    research_item_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("research_items.id", ondelete="SET NULL"), nullable=True, index=True
    )
    platform: Mapped[str] = mapped_column(String(20), nullable=False)
    language: Mapped[str] = mapped_column(String(12), default="en", nullable=False)
    title: Mapped[str | None] = mapped_column(String(300))
    body: Mapped[str] = mapped_column(Text, nullable=False)
    hashtags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    media_urls: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    generation_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="draft", nullable=False)

    research_item: Mapped["ResearchItem | None"] = relationship(back_populates="drafts")
    approval: Mapped["Approval | None"] = relationship(
        back_populates="content_draft", uselist=False, cascade="all, delete-orphan"
    )
    publishing_records: Mapped[list["PublishingRecord"]] = relationship(
        back_populates="content_draft"
    )
