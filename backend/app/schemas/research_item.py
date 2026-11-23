from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, model_validator

from app.schemas.common import ORMModel

ResearchStatus = Literal["new", "reviewed", "rejected", "used"]

class ResearchItemCreate(BaseModel):
    source_id: UUID | None = None
    title: str = Field(min_length=1, max_length=500)
    url: HttpUrl | None = None
    summary: str | None = None
    content: str | None = None
    content_hash: str | None = Field(default=None, min_length=1, max_length=64)
    topic: str | None = Field(default=None, max_length=120)
    language: str = Field(default="en", min_length=2, max_length=12)
    status: ResearchStatus = "new"
    relevance_score: float | None = Field(default=None, ge=0, le=1)
    published_at: datetime | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)

class ResearchItemUpdate(BaseModel):
    source_id: UUID | None = None
    title: str | None = Field(default=None, min_length=1, max_length=500)
    url: HttpUrl | None = None
    summary: str | None = None
    content: str | None = None
    content_hash: str | None = Field(default=None, min_length=1, max_length=64)
    topic: str | None = Field(default=None, max_length=120)
    language: str | None = Field(default=None, min_length=2, max_length=12)
    status: ResearchStatus | None = None
    relevance_score: float | None = Field(default=None, ge=0, le=1)
    published_at: datetime | None = None
    metadata_json: dict[str, Any] | None = None

    @model_validator(mode="after")
    def reject_null_for_required_fields(self):
        for field in ("title", "language", "status", "metadata_json"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null.")
        return self

class ResearchItemRead(ORMModel):
    id: UUID
    source_id: UUID | None
    title: str
    url: str | None
    summary: str | None
    content: str | None
    content_hash: str | None
    topic: str | None
    language: str
    status: str
    relevance_score: float | None
    published_at: datetime | None
    discovered_at: datetime
    metadata_json: dict[str, Any]
    created_at: datetime
    updated_at: datetime
