from fastapi import APIRouter, Depends, HTTPException, status
from openai import OpenAIError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_admin
from app.db.session import get_db_session
from app.models.content_draft import ContentDraft
from app.models.research_item import ResearchItem
from app.schemas.content_generation import (
    ContentGenerationRequest,
    ContentGenerationResponse,
)
from app.services.content_generation import ContentGenerator, get_content_generator

router = APIRouter(
    prefix="/content-generation",
    tags=["Content Generation"],
    dependencies=[Depends(require_admin)],
)


@router.post(
    "/generate",
    response_model=ContentGenerationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_content(
    payload: ContentGenerationRequest,
    session: AsyncSession = Depends(get_db_session),
    generator: ContentGenerator = Depends(get_content_generator),
):
    research_item = await session.scalar(
        select(ResearchItem).where(ResearchItem.id == payload.research_item_id)
    )
    if research_item is None:
        raise HTTPException(status_code=404, detail="Research item not found.")

    generated: list[ContentDraft] = []
    try:
        for platform in payload.platforms:
            post = await generator.generate(
                research_item=research_item,
                platform=platform,
                language=payload.language,
                tone=payload.tone,
                target_audience=payload.target_audience,
                call_to_action=payload.call_to_action,
            )
            generated.append(
                ContentDraft(
                    research_item_id=research_item.id,
                    platform=platform,
                    language=payload.language,
                    title=post.title,
                    body=post.body,
                    hashtags=post.hashtags,
                    generation_metadata={
                        "provider": getattr(generator, "provider", "test-provider"),
                        "model": getattr(generator, "model", "test-provider"),
                        "research_item_id": str(research_item.id),
                    },
                    status="draft",
                )
            )
    except OpenAIError:
        raise HTTPException(
            status_code=502,
            detail="The AI provider request failed. No drafts were saved.",
        ) from None
    except ValueError:
        raise HTTPException(
            status_code=502,
            detail="The AI provider returned invalid content. No drafts were saved.",
        ) from None

    session.add_all(generated)
    await session.commit()
    for draft in generated:
        await session.refresh(draft)
    return {"drafts": generated}
