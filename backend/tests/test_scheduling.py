from datetime import UTC, datetime, timedelta

from httpx import AsyncClient


async def _approved_draft(client: AsyncClient) -> str:
    draft = await client.post(
        "/api/v1/content-drafts",
        json={
            "platform": "linkedin",
            "language": "en",
            "title": "Scheduling test",
            "body": "An approved draft for scheduling.",
        },
    )
    assert draft.status_code == 201
    draft_id = draft.json()["id"]
    approval = await client.post(
        f"/api/v1/content-drafts/{draft_id}/submit-for-approval"
    )
    assert approval.status_code == 201
    decision = await client.post(
        f"/api/v1/approvals/{approval.json()['id']}/decision",
        json={"decision": "approved"},
    )
    assert decision.status_code == 200
    return draft_id


async def test_schedule_requires_approved_draft(client: AsyncClient) -> None:
    draft = await client.post(
        "/api/v1/content-drafts",
        json={"platform": "x", "language": "en", "body": "Not approved yet."},
    )
    response = await client.post(
        "/api/v1/publishing/schedules",
        json={
            "content_draft_id": draft.json()["id"],
            "scheduled_at": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
        },
    )
    assert response.status_code == 409


async def test_create_list_and_cancel_schedule(client: AsyncClient) -> None:
    draft_id = await _approved_draft(client)
    scheduled_at = datetime.now(UTC) + timedelta(days=1)
    created = await client.post(
        "/api/v1/publishing/schedules",
        json={"content_draft_id": draft_id, "scheduled_at": scheduled_at.isoformat()},
    )
    assert created.status_code == 201
    record = created.json()
    assert record["status"] == "queued"
    assert record["platform"] == "linkedin"

    duplicate_time = scheduled_at + timedelta(hours=1)
    duplicate = await client.post(
        "/api/v1/publishing/schedules",
        json={
            "content_draft_id": draft_id,
            "scheduled_at": duplicate_time.isoformat(),
        },
    )
    assert duplicate.status_code == 409

    listed = await client.get("/api/v1/publishing/schedules?status=queued")
    assert listed.status_code == 200
    assert any(item["id"] == record["id"] for item in listed.json()["items"])

    cancelled = await client.delete(f"/api/v1/publishing/schedules/{record['id']}")
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"

    draft = await client.get(f"/api/v1/content-drafts/{draft_id}")
    assert draft.json()["status"] == "approved"


async def test_schedule_rejects_naive_or_past_datetime(client: AsyncClient) -> None:
    draft_id = await _approved_draft(client)
    naive = await client.post(
        "/api/v1/publishing/schedules",
        json={"content_draft_id": draft_id, "scheduled_at": "2035-01-01T10:00:00"},
    )
    assert naive.status_code == 422

    past = await client.post(
        "/api/v1/publishing/schedules",
        json={"content_draft_id": draft_id, "scheduled_at": "2020-01-01T10:00:00+00:00"},
    )
    assert past.status_code == 422


async def test_schedule_requires_admin(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/publishing/schedules",
        headers={"Authorization": ""},
    )
    assert response.status_code == 401
