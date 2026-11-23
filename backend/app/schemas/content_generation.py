from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.schemas.content_draft import ContentDraftRead

Platform = Literal["linkedin", "instagram", "x"]


class ContentGenerationRequest(BaseModel):
    research_item_id: str
    platforms: list[Platform] = Field(min_length=1, max_length=3)
    language: str = Field(default="en", min_length=2, max_length=12)
    tone: str = Field(default="informative and engaging", min_length=3, max_length=120)
    target_audience: str = Field(
        default="technology-interested professionals",
        min_length=3,
        max_length=200,
    )
    call_to_action: str | None = Field(default=None, max_length=240)

    @model_validator(mode="after")
    def platforms_must_be_unique(self):
        if len(self.platforms) != len(set(self.platforms)):
            raise ValueError("Platforms must not contain duplicates.")
        return self


class GeneratedPost(BaseModel):
    title: str | None = Field(default=None, max_length=300)
    body: str = Field(min_length=1)
    hashtags: list[str] = Field(default_factory=list, max_length=15)


class ContentGenerationResponse(BaseModel):
    drafts: list[ContentDraftRead]
