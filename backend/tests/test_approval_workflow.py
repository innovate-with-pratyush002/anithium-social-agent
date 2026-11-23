from httpx import AsyncClient


async def create_draft(client: AsyncClient) -> str:
    response = await client.post(
        "/api/v1/content-drafts",
        json={
            "platform": "linkedin",
            "language": "en",
            "title": "Approval workflow test",
            "body": "A draft that must be reviewed before publishing.",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


async def test_submit_request_changes_and_approve(client: AsyncClient) -> None:
    draft_id = await create_draft(client)

    submitted = await client.post(
        f"/api/v1/content-drafts/{draft_id}/submit-for-approval"
    )
    assert submitted.status_code == 201
    approval = submitted.json()
    approval_id = approval["id"]
    assert approval["status"] == "pending"
    assert approval["content_draft"]["status"] == "pending_approval"

    duplicate_submission = await client.post(
        f"/api/v1/content-drafts/{draft_id}/submit-for-approval"
    )
    assert duplicate_submission.status_code == 409

    missing_feedback = await client.post(
        f"/api/v1/approvals/{approval_id}/decision",
        json={"decision": "changes_requested"},
    )
    assert missing_feedback.status_code == 422

    changes_requested = await client.post(
        f"/api/v1/approvals/{approval_id}/decision",
        json={
            "decision": "changes_requested",
            "feedback": "Add a concrete example and a stronger opening.",
        },
    )
    assert changes_requested.status_code == 200
    assert changes_requested.json()["status"] == "changes_requested"
    assert changes_requested.json()["content_draft"]["status"] == "draft"

    updated = await client.patch(
        f"/api/v1/content-drafts/{draft_id}",
        json={"body": "Updated with a concrete example and stronger opening."},
    )
    assert updated.status_code == 200

    resubmitted = await client.post(
        f"/api/v1/content-drafts/{draft_id}/submit-for-approval"
    )
    assert resubmitted.status_code == 201
    assert resubmitted.json()["id"] == approval_id
    assert resubmitted.json()["status"] == "pending"

    approved = await client.post(
        f"/api/v1/approvals/{approval_id}/decision",
        json={"decision": "approved"},
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"
    assert approved.json()["reviewer_id"] is not None
    assert approved.json()["reviewed_at"] is not None
    assert approved.json()["content_draft"]["status"] == "approved"

    edit_approved = await client.patch(
        f"/api/v1/content-drafts/{draft_id}",
        json={"body": "This edit must not be allowed."},
    )
    assert edit_approved.status_code == 409

    submit_approved = await client.post(
        f"/api/v1/content-drafts/{draft_id}/submit-for-approval"
    )
    assert submit_approved.status_code == 409


async def test_list_pending_approvals(client: AsyncClient) -> None:
    draft_id = await create_draft(client)
    submitted = await client.post(
        f"/api/v1/content-drafts/{draft_id}/submit-for-approval"
    )
    assert submitted.status_code == 201

    response = await client.get("/api/v1/approvals", params={"status": "pending"})
    assert response.status_code == 200
    assert response.json()["pagination"]["total"] >= 1
    assert any(
        item["content_draft_id"] == draft_id for item in response.json()["items"]
    )
