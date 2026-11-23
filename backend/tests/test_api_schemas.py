from uuid import UUID

import pytest
from pydantic import ValidationError

from app.schemas.content_draft import ContentDraftCreate
from app.schemas.research_item import ResearchItemCreate
from app.schemas.source import SourceCreate


def test_source_schema_validates_http_url() -> None:
    source = SourceCreate(
        name="OpenAI Blog",
        source_type="rss",
        url="https://openai.com/blog",
    )
    assert str(source.url).startswith("https://openai.com/")


def test_research_item_accepts_uuid_and_bounded_relevance() -> None:
    source_id = UUID("8b2f2d40-c31e-4d2a-a8db-5e9f9c31b2a4")
    item = ResearchItemCreate(source_id=source_id, title="AI research", relevance_score=0.85)
    assert item.source_id == source_id
    with pytest.raises(ValidationError):
        ResearchItemCreate(title="Invalid score", relevance_score=1.5)


def test_content_draft_rejects_unsupported_platform() -> None:
    with pytest.raises(ValidationError):
        ContentDraftCreate(platform="threads", body="Hello world")


def test_content_draft_defaults_collections_and_keeps_status_server_managed() -> None:
    draft = ContentDraftCreate(platform="linkedin", body="Anithium update")
    assert "status" not in ContentDraftCreate.model_fields
    assert draft.hashtags == []
    assert draft.media_urls == []
