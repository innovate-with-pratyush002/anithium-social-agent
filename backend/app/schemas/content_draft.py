from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import ORMModel

Platform = Literal["linkedin", "instagram", "x"]
DraftStatus = Literal[
    "draft", "pending_approval", "approved", "scheduled", "published", "failed", "archived"
]


class ContentDraftCreate(BaseModel):
    research_item_id: UUID | None = None
    platform: Platform
    language: str = Field(default="en", min_length=2, max_length=12)
    title: str | None = Field(default=None, max_length=300)
    body: str = Field(min_length=1)
    hashtags: list[str] = Field(default_factory=list)
    media_urls: list[str] = Field(default_factory=list)
    generation_metadata: dict[str, Any] = Field(default_factory=dict)


class ContentDraftUpdate(BaseModel):
    research_item_id: UUID | None = None
    platform: Platform | None = None
    language: str | None = Field(default=None, min_length=2, max_length=12)
    title: str | None = Field(default=None, max_length=300)
    body: str | None = Field(default=None, min_length=1)
    hashtags: list[str] | None = None
    media_urls: list[str] | None = None
    generation_metadata: dict[str, Any] | None = None

    @model_validator(mode="after")
    def reject_null_for_required_fields(self):
        for field in (
            "platform",
            "language",
            "body",
            "hashtags",
            "media_urls",
            "generation_metadata",
        ):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null.")
        return self


class ContentDraftRead(ORMModel):
    id: UUID
    research_item_id: UUID | None
    platform: str
    language: str
    title: str | None
    body: str
    hashtags: list[str]
    media_urls: list[str]
    generation_metadata: dict[str, Any]
    status: str
    created_at: datetime
    updated_at: datetime
