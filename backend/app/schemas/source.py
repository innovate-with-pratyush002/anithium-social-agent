from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, model_validator

from app.schemas.common import ORMModel


class SourceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    source_type: str = Field(min_length=1, max_length=30)
    url: HttpUrl
    description: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    reliability_score: float = Field(default=0.7, ge=0, le=1)


class SourceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    source_type: str | None = Field(default=None, min_length=1, max_length=30)
    url: HttpUrl | None = None
    description: str | None = None
    config: dict[str, Any] | None = None
    is_active: bool | None = None
    reliability_score: float | None = Field(default=None, ge=0, le=1)

    @model_validator(mode="after")
    def reject_null_for_required_fields(self):
        for field in (
            "name",
            "source_type",
            "url",
            "config",
            "is_active",
            "reliability_score",
        ):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null.")
        return self


class SourceRead(ORMModel):
    id: UUID
    name: str
    source_type: str
    url: str
    description: str | None
    config: dict[str, Any]
    is_active: bool
    reliability_score: float
    created_by_id: UUID | None
    created_at: datetime
    updated_at: datetime
