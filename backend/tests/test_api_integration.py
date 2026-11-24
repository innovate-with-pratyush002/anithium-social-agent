from httpx import AsyncClient


async def test_source_crud_and_duplicate_conflict(client: AsyncClient) -> None:
    payload = {
        "name": "Anithium Engineering Blog",
        "source_type": "rss",
        "url": "https://example.com/engineering-feed.xml",
        "description": "Technology research feed",
    }
    created = await client.post("/api/v1/sources", json=payload)

    assert created.status_code == 201
    source = created.json()
    source_id = source["id"]
    assert source["name"] == payload["name"]
    assert source["is_active"] is True
    assert source["reliability_score"] == 0.7

    duplicate = await client.post("/api/v1/sources", json=payload)
    assert duplicate.status_code == 409

    listed = await client.get("/api/v1/sources", params={"active": "true"})
    assert listed.status_code == 200
    assert listed.json()["pagination"]["total"] >= 1
    assert any(item["id"] == source_id for item in listed.json()["items"])

    updated = await client.patch(
        f"/api/v1/sources/{source_id}",
        json={"description": "Updated research feed"},
    )
    assert updated.status_code == 200
    assert updated.json()["description"] == "Updated research feed"

    reliability_update = await client.patch(
        f"/api/v1/sources/{source_id}", json={"reliability_score": 0.91}
    )
    assert reliability_update.status_code == 200
    assert reliability_update.json()["reliability_score"] == 0.91

    invalid_reliability = await client.patch(
        f"/api/v1/sources/{source_id}", json={"reliability_score": 1.2}
    )
    assert invalid_reliability.status_code == 422

    deactivated = await client.delete(f"/api/v1/sources/{source_id}")
    assert deactivated.status_code == 204

    fetched = await client.get(f"/api/v1/sources/{source_id}")
    assert fetched.status_code == 200
    assert fetched.json()["is_active"] is False


async def test_research_item_crud_and_filters(client: AsyncClient) -> None:
    source_response = await client.post(
        "/api/v1/sources",
        json={
            "name": "Research Source",
            "source_type": "website",
            "url": "https://example.com/research",
        },
    )
    assert source_response.status_code == 201
    source_id = source_response.json()["id"]

    payload = {
        "source_id": source_id,
        "title": "Practical AI Agents",
        "url": "https://example.com/articles/ai-agents",
        "summary": "An overview of agent architectures.",
        "topic": "AI",
        "relevance_score": 0.92,
    }
    created = await client.post("/api/v1/research-items", json=payload)

    assert created.status_code == 201
    item_id = created.json()["id"]
    assert created.json()["status"] == "new"

    listed = await client.get(
        "/api/v1/research-items",
        params={"topic": "AI", "source_id": source_id},
    )
    assert listed.status_code == 200
    assert any(item["id"] == item_id for item in listed.json()["items"])

    updated = await client.patch(
        f"/api/v1/research-items/{item_id}",
        json={"status": "reviewed", "relevance_score": 0.98},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "reviewed"
    assert updated.json()["relevance_score"] == 0.98

    missing = await client.get("/api/v1/research-items/00000000-0000-0000-0000-000000000001")
    assert missing.status_code == 404


async def test_content_draft_crud(client: AsyncClient) -> None:
    payload = {
        "platform": "linkedin",
        "language": "en",
        "title": "AI is changing software development",
        "body": "A concise draft about practical AI workflows.",
        "hashtags": ["AI", "SoftwareEngineering"],
    }
    created = await client.post("/api/v1/content-drafts", json=payload)

    assert created.status_code == 201
    draft_id = created.json()["id"]
    assert created.json()["status"] == "draft"

    listed = await client.get(
        "/api/v1/content-drafts",
        params={"platform": "linkedin", "status": "draft"},
    )
    assert listed.status_code == 200
    assert any(draft["id"] == draft_id for draft in listed.json()["items"])

    updated = await client.patch(
        f"/api/v1/content-drafts/{draft_id}",
        json={"body": "Updated draft content."},
    )
    assert updated.status_code == 200
    assert updated.json()["body"] == "Updated draft content."

    deleted = await client.delete(f"/api/v1/content-drafts/{draft_id}")
    assert deleted.status_code == 204

    missing = await client.get(f"/api/v1/content-drafts/{draft_id}")
    assert missing.status_code == 404
