from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ResearchIntelligenceRequest(BaseModel):
    max_items: int = Field(default=10, ge=1, le=20)
    research_item_ids: list[UUID] | None = Field(default=None, max_length=20)
    retry_failed: bool = False


class ResearchAnalysis(BaseModel):
    summary: str = Field(min_length=20, max_length=1500)
    topic: str = Field(min_length=2, max_length=120)
    language: str = Field(min_length=2, max_length=12)
    relevance_score: float = Field(ge=0, le=1)
    key_points: list[str] = Field(default_factory=list, max_length=5)


class ResearchAnalysisResult(BaseModel):
    research_item_id: UUID
    title: str
    status: str
    relevance_score: float | None = None
    error: str | None = None


class ResearchIntelligenceResponse(BaseModel):
    started_at: datetime
    completed_at: datetime
    processed: int
    analyzed: int
    failed: int
    results: list[ResearchAnalysisResult]


class ResearchTrend(BaseModel):
    topic: str
    item_count: int
    average_relevance: float
    latest_discovered_at: datetime


class ResearchTrendsResponse(BaseModel):
    window_days: int
    trends: list[ResearchTrend]
