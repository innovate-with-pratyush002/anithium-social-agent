from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import PageMeta

EditorialPlatform = Literal["linkedin", "instagram", "x"]


class PlatformOpportunity(BaseModel):
    platform: EditorialPlatform
    angle: str
    suggested_format: str
    rationale: str


class ContentOpportunity(BaseModel):
    research_item_id: UUID
    title: str
    topic: str | None
    summary: str | None
    relevance_score: float | None
    quality_score: float | None
    opportunity_score: float = Field(ge=0, le=1)
    opportunity_reason: str
    available_platforms: list[PlatformOpportunity]


class EditorialOpportunitiesResponse(BaseModel):
    items: list[ContentOpportunity]
    pagination: PageMeta
    window_days: int
