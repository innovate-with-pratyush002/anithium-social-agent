from uuid import uuid4

from httpx import AsyncClient

from app.main import app
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
    app.dependency_overrides[get_content_generator] = lambda: FakeContentGenerator()
    try:
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
    finally:
        app.dependency_overrides.pop(get_content_generator, None)


async def test_generate_content_rejects_unknown_research_item(client: AsyncClient) -> None:
    app.dependency_overrides[get_content_generator] = lambda: FakeContentGenerator()
    try:
        response = await client.post(
            "/api/v1/content-generation/generate",
            json={
                "research_item_id": str(uuid4()),
                "platforms": ["linkedin"],
            },
        )
        assert response.status_code == 404
    finally:
        app.dependency_overrides.pop(get_content_generator, None)


async def test_generate_content_rejects_duplicate_platforms(client: AsyncClient) -> None:
    app.dependency_overrides[get_content_generator] = lambda: FakeContentGenerator()
    try:
        response = await client.post(
            "/api/v1/content-generation/generate",
            json={
                "research_item_id": str(uuid4()),
                "platforms": ["linkedin", "linkedin"],
            },
        )
        assert response.status_code == 422
    finally:
        app.dependency_overrides.pop(get_content_generator, None)


def test_groq_provider_is_selected_from_settings(monkeypatch) -> None:
    from types import SimpleNamespace

    import app.services.content_generation as service

    monkeypatch.setattr(
        service,
        "get_settings",
        lambda: SimpleNamespace(
            ai_provider="groq",
            groq_api_key="test-groq-key",
            groq_model="openai/gpt-oss-20b",
        ),
    )

    generator = service.get_content_generator()

    assert generator.provider == "groq"
    assert generator.model == "openai/gpt-oss-20b"
    assert str(generator.client.base_url).rstrip("/") == "https://api.groq.com/openai/v1"


def test_gemini_provider_can_be_selected_from_settings(monkeypatch) -> None:
    from types import SimpleNamespace

    import app.services.content_generation as service

    monkeypatch.setattr(
        service,
        "get_settings",
        lambda: SimpleNamespace(
            ai_provider="gemini",
            gemini_api_key="test-gemini-key",
            gemini_model="gemini-test-model",
        ),
    )

    generator = service.get_content_generator()

    assert generator.provider == "gemini"
    assert generator.model == "gemini-test-model"
    assert str(generator.client.base_url).rstrip("/") == (
        "https://generativelanguage.googleapis.com/v1beta/openai"
    )


def test_selected_provider_requires_its_own_api_key(monkeypatch) -> None:
    from types import SimpleNamespace

    from fastapi import HTTPException
    import pytest

    import app.services.content_generation as service

    monkeypatch.setattr(
        service,
        "get_settings",
        lambda: SimpleNamespace(
            ai_provider="groq",
            groq_api_key=None,
            groq_model="openai/gpt-oss-20b",
        ),
    )

    with pytest.raises(HTTPException) as error:
        service.get_content_generator()

    assert error.value.status_code == 503
    assert "GROQ_API_KEY" in error.value.detail
