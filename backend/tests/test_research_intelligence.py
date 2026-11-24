from httpx import AsyncClient

from app.main import app
from app.schemas.research_intelligence import ResearchAnalysis
from app.services.research_intelligence import get_research_analyzer


class FakeResearchAnalyzer:
    provider = "test-provider"
    model = "test-model"

    async def analyze(self, item):
        return ResearchAnalysis(
            summary=f"Analysis summary for {item.title}. This is grounded in supplied metadata.",
            topic="Artificial Intelligence",
            language="en",
            relevance_score=0.92,
            key_points=["AI tooling", "Developer productivity"],
        )


async def _create_research_item(client: AsyncClient) -> str:
    response = await client.post(
        "/api/v1/research-items",
        json={
            "title": "AI coding agents for modern developers",
            "summary": "<p>Agents can help developers automate coding tasks.</p>",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


async def test_research_intelligence_analyzes_and_ranks_items(
    client: AsyncClient,
) -> None:
    research_id = await _create_research_item(client)
    app.dependency_overrides[get_research_analyzer] = lambda: FakeResearchAnalyzer()
    try:
        response = await client.post(
            "/api/v1/research-intelligence/analyze",
            json={"max_items": 1, "research_item_ids": [research_id]},
        )
        assert response.status_code == 200
        assert response.json()["analyzed"] == 1
        assert response.json()["failed"] == 0
    finally:
        app.dependency_overrides.pop(get_research_analyzer, None)

    ranked = await client.get("/api/v1/research-intelligence/ranked")
    assert ranked.status_code == 200
    item = next(item for item in ranked.json()["items"] if item["id"] == research_id)
    assert item["summary"].startswith("Analysis summary")
    assert item["topic"] == "Artificial Intelligence"
    assert item["relevance_score"] == 0.92
    assert 0 <= item["quality_score"] <= 1
    assert "descriptive_title" in item["quality_signals"]
    assert item["metadata_json"]["intelligence"]["provider"] == "test-provider"


async def test_research_intelligence_skips_already_analyzed_items(
    client: AsyncClient,
) -> None:
    research_id = await _create_research_item(client)
    app.dependency_overrides[get_research_analyzer] = lambda: FakeResearchAnalyzer()
    try:
        first = await client.post(
            "/api/v1/research-intelligence/analyze",
            json={"research_item_ids": [research_id]},
        )
        assert first.status_code == 200
        assert first.json()["analyzed"] == 1

        second = await client.post(
            "/api/v1/research-intelligence/analyze",
            json={"research_item_ids": [research_id]},
        )
        assert second.status_code == 200
        assert second.json()["processed"] == 0
    finally:
        app.dependency_overrides.pop(get_research_analyzer, None)


async def test_research_intelligence_requires_admin(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/research-intelligence/analyze",
        json={},
        headers={"Authorization": ""},
    )
    assert response.status_code == 401


class FailingResearchAnalyzer:
    provider = "test-provider"
    model = "test-model"

    async def analyze(self, item):
        raise ValueError("Temporary provider response error")


async def test_failed_analysis_retry_limit_is_enforced(client: AsyncClient) -> None:
    research_id = await _create_research_item(client)
    app.dependency_overrides[get_research_analyzer] = lambda: FailingResearchAnalyzer()
    try:
        for expected_attempt in (1, 2, 3):
            response = await client.post(
                "/api/v1/research-intelligence/analyze",
                json={"research_item_ids": [research_id], "retry_failed": expected_attempt > 1},
            )
            assert response.status_code == 200
            assert response.json()["failed"] == 1

        exhausted = await client.post(
            "/api/v1/research-intelligence/analyze",
            json={"research_item_ids": [research_id], "retry_failed": True},
        )
        assert exhausted.status_code == 200
        assert exhausted.json()["processed"] == 0
    finally:
        app.dependency_overrides.pop(get_research_analyzer, None)

    item = await client.get(f"/api/v1/research-items/{research_id}")
    assert item.json()["analysis_status"] == "failed"
    assert item.json()["analysis_attempts"] == 3
    assert item.json()["analysis_error"] == "Temporary provider response error"


async def test_research_trends_require_two_analyzed_items(client: AsyncClient) -> None:
    first_id = await _create_research_item(client)
    second_id = await _create_research_item(client)
    app.dependency_overrides[get_research_analyzer] = lambda: FakeResearchAnalyzer()
    try:
        response = await client.post(
            "/api/v1/research-intelligence/analyze",
            json={"research_item_ids": [first_id, second_id]},
        )
        assert response.status_code == 200
        assert response.json()["analyzed"] == 2
    finally:
        app.dependency_overrides.pop(get_research_analyzer, None)

    trends = await client.get("/api/v1/research-intelligence/trends")
    assert trends.status_code == 200
    assert trends.json()["trends"][0]["topic"] == "Artificial Intelligence"
    assert trends.json()["trends"][0]["item_count"] >= 2
