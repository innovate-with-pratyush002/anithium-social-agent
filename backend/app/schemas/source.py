from datetime import datetime
from typing import Any

from pydantic import Field, HttpUrl

from app.schemas.common import ORMModel

class SourceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    source_type: str = Field(min_length=1, max_length=30)
    url: HttpUrl
    description: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True

class SourceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    source_type: str | None = Field(default=None, min_length=1, max_length=30)
    url: HttpUrl | None = None
    description: str | None = None
    config: dict[str, Any] | None = None
    is_active: bool | None = None

class SourceRead(ORMModel):
    id: str
    name: str
    source_type: str
    url: str
    description: str | None
    config: dict[str, Any]
    is_active: bool
    created_by_id: str | None
    created_at: datetime
    updated_at: datetime
