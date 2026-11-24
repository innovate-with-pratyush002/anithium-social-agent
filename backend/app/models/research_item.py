import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Index, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.content_draft import ContentDraft
    from app.models.source import Source


class ResearchItem(TimestampMixin, Base):
    __tablename__ = "research_items"
    __table_args__ = (
        Index("ix_research_items_status_published_at", "status", "published_at"),
        Index("ix_research_items_analysis_status", "analysis_status"),
        Index("ix_research_items_topic_discovered", "topic", "discovered_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("sources.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str | None] = mapped_column(String(2048), unique=True)
    summary: Mapped[str | None] = mapped_column(Text)
    content: Mapped[str | None] = mapped_column(Text)
    content_hash: Mapped[str | None] = mapped_column(String(64), unique=True)
    topic: Mapped[str | None] = mapped_column(String(120), index=True)
    language: Mapped[str] = mapped_column(String(12), default="en", nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="new", nullable=False)
    relevance_score: Mapped[float | None]
    quality_score: Mapped[float | None] = mapped_column(Float)
    quality_signals: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    analysis_status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    analysis_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    analysis_error: Mapped[str | None] = mapped_column(Text)
    analyzed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    source: Mapped["Source | None"] = relationship(back_populates="research_items")
    drafts: Mapped[list["ContentDraft"]] = relationship(back_populates="research_item")
