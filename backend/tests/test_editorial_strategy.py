from httpx import AsyncClient

from app.main import app
from app.schemas.research_intelligence import ResearchAnalysis
from app.services.research_intelligence import get_research_analyzer


class EditorialTestAnalyzer:
    provider = "test-provider"
    model = "test-model"

    async def analyze(self, item):
        return ResearchAnalysis(
            summary="A grounded summary of the source material for editorial testing.",
            topic="Artificial Intelligence",
            language="en",
            relevance_score=0.9,
            key_points=["A supported research point"],
        )


async def _create_analyzed_research(client: AsyncClient) -> str:
    created = await client.post(
        "/api/v1/research-items",
        json={
            "title": "A recent development in AI developer tools",
            "summary": "The source describes a new capability for software developers.",
        },
    )
    assert created.status_code == 201
    research_id = created.json()["id"]

    app.dependency_overrides[get_research_analyzer] = lambda: EditorialTestAnalyzer()
    try:
        analyzed = await client.post(
            "/api/v1/research-intelligence/analyze",
            json={"research_item_ids": [research_id], "max_items": 1},
        )
        assert analyzed.status_code == 200
        assert analyzed.json()["analyzed"] == 1
    finally:
        app.dependency_overrides.pop(get_research_analyzer, None)
    return research_id


async def test_editorial_opportunities_provide_platform_specific_angles(
    client: AsyncClient,
) -> None:
    research_id = await _create_analyzed_research(client)

    response = await client.get("/api/v1/editorial/opportunities")
    assert response.status_code == 200
    payload = response.json()
    assert payload["pagination"]["total"] >= 1

    item = next(entry for entry in payload["items"] if entry["research_item_id"] == research_id)
    assert 0 <= item["opportunity_score"] <= 1
    assert {entry["platform"] for entry in item["available_platforms"]} == {
        "linkedin",
        "instagram",
        "x",
    }
    assert all(
        entry["angle"] and entry["suggested_format"] for entry in item["available_platforms"]
    )


async def test_editorial_opportunities_exclude_platforms_with_existing_drafts(
    client: AsyncClient,
) -> None:
    research_id = await _create_analyzed_research(client)
    draft = await client.post(
        "/api/v1/content-drafts",
        json={
            "research_item_id": research_id,
            "platform": "linkedin",
            "language": "en",
            "body": "An existing LinkedIn draft for this research.",
        },
    )
    assert draft.status_code == 201

    response = await client.get(
        "/api/v1/editorial/opportunities?platforms=linkedin&platforms=x"
    )
    assert response.status_code == 200
    item = next(
        entry for entry in response.json()["items"] if entry["research_item_id"] == research_id
    )
    assert [entry["platform"] for entry in item["available_platforms"]] == ["x"]


async def test_editorial_opportunities_require_admin(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/editorial/opportunities",
        headers={"Authorization": ""},
    )
    assert response.status_code == 401


async def test_editorial_opportunities_validate_query_limits(client: AsyncClient) -> None:
    response = await client.get("/api/v1/editorial/opportunities?window_days=0")
    assert response.status_code == 422
