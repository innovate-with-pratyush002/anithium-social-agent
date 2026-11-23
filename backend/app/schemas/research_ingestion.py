from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ResearchIngestionRequest(BaseModel):
    source_ids: list[UUID] | None = Field(default=None, max_length=50)
    max_items_per_source: int = Field(default=20, ge=1, le=50)


class SourceIngestionResult(BaseModel):
    source_id: UUID
    source_name: str
    status: str
    fetched: int = 0
    created: int = 0
    duplicates: int = 0
    errors: list[str] = Field(default_factory=list)


class ResearchIngestionResponse(BaseModel):
    started_at: datetime
    completed_at: datetime
    sources_processed: int
    fetched: int
    created: int
    duplicates: int
    failed_sources: int
    results: list[SourceIngestionResult]
