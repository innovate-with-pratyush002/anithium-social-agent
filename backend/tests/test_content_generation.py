from uuid import uuid4

from httpx import AsyncClient

from app.schemas.content_generation import GeneratedPost
from app.services.content_generation import get_content_generator


class FakeContentGenerator:
    model = "fake-model"

    async def generate(
        self,
        research_item,
        platform,
        language,
        tone,
        target_audience,
        call_to_action,
    ):
        return GeneratedPost(
            title=f"{platform.title()} post",
            body=f"Generated {platform} content about {research_item.title}.",
            hashtags=["AI", "Anithium"],
        )


async def test_generate_platform_drafts(client: AsyncClient) -> None:
    client._transport.app.dependency_overrides[get_content_generator] = (
        lambda: FakeContentGenerator()
    )
    research = await client.post(
        "/api/v1/research-items",
        json={
            "title": "Practical AI Agents",
            "summary": "AI agents can plan and use tools to complete tasks.",
            "topic": "AI",
        },
    )
    assert research.status_code == 201
    research_id = research.json()["id"]

    response = await client.post(
        "/api/v1/content-generation/generate",
        json={
            "research_item_id": research_id,
            "platforms": ["linkedin", "instagram", "x"],
            "language": "en",
        },
    )
    assert response.status_code == 201
    drafts = response.json()["drafts"]
    assert len(drafts) == 3
    assert {draft["platform"] for draft in drafts} == {"linkedin", "instagram", "x"}
    assert all(draft["status"] == "draft" for draft in drafts)
    assert all(draft["research_item_id"] == research_id for draft in drafts)
    client._transport.app.dependency_overrides.pop(get_content_generator, None)


async def test_generate_content_rejects_unknown_research_item(client: AsyncClient) -> None:
    client._transport.app.dependency_overrides[get_content_generator] = (
        lambda: FakeContentGenerator()
    )
    response = await client.post(
        "/api/v1/content-generation/generate",
        json={
            "research_item_id": str(uuid4()),
            "platforms": ["linkedin"],
        },
    )
    assert response.status_code == 404
    client._transport.app.dependency_overrides.pop(get_content_generator, None)


async def test_generate_content_rejects_duplicate_platforms(client: AsyncClient) -> None:
    client._transport.app.dependency_overrides[get_content_generator] = (
        lambda: FakeContentGenerator()
    )
    response = await client.post(
        "/api/v1/content-generation/generate",
        json={
            "research_item_id": str(uuid4()),
            "platforms": ["linkedin", "linkedin"],
        },
    )
    assert response.status_code == 422
    client._transport.app.dependency_overrides.pop(get_content_generator, None)
