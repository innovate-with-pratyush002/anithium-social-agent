from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from app.schemas.common import ORMModel

Platform = Literal["linkedin", "instagram", "x"]
DraftStatus = Literal[
    "draft", "pending_approval", "approved", "scheduled", "published", "failed", "archived"
]

class ContentDraftCreate(BaseModel):
    research_item_id: str | None = None
    platform: Platform
    language: str = Field(default="en", min_length=2, max_length=12)
    title: str | None = Field(default=None, max_length=300)
    body: str = Field(min_length=1)
    hashtags: list[str] = Field(default_factory=list)
    media_urls: list[str] = Field(default_factory=list)
    generation_metadata: dict[str, Any] = Field(default_factory=dict)
    status: DraftStatus = "draft"

class ContentDraftUpdate(BaseModel):
    research_item_id: str | None = None
    platform: Platform | None = None
    language: str | None = Field(default=None, min_length=2, max_length=12)
    title: str | None = Field(default=None, max_length=300)
    body: str | None = Field(default=None, min_length=1)
    hashtags: list[str] | None = None
    media_urls: list[str] | None = None
    generation_metadata: dict[str, Any] | None = None
    status: DraftStatus | None = None

class ContentDraftRead(ORMModel):
    id: str
    research_item_id: str | None
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
