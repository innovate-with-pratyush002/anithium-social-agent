# Phase 5 — Content Approval Workflow

## Purpose

Content drafts must be reviewed by an administrator before they can become eligible for publishing. The approval record is the review decision; the content draft status is advanced by server-side workflow operations rather than client-supplied status values.

## Workflow

1. A new content draft is created with status `draft`.
2. The administrator submits it for review.
3. The draft becomes `pending_approval` and an approval record is created with status `pending`.
4. The administrator records one of three decisions:
   - `approved`: approval becomes approved and the draft becomes approved.
   - `rejected`: approval becomes rejected and the draft returns to draft.
   - `changes_requested`: approval becomes changes_requested and the draft returns to draft for editing.
5. A draft returned to draft after rejection or requested changes can be edited and resubmitted. The current approval record is reused; this model stores the latest review state, not a full decision history.

Only an administrator can access the content workspace and approval endpoints.

## Endpoints

- `POST /api/v1/content-drafts/{draft_id}/submit-for-approval`
- `GET /api/v1/approvals?status=pending`
- `GET /api/v1/approvals/{approval_id}`
- `POST /api/v1/approvals/{approval_id}/decision`

Decision request examples:

Approve:

```json
{
  "decision": "approved"
}
```

Reject or request changes (feedback is required):

```json
{
  "decision": "changes_requested",
  "feedback": "Add a concrete example and revise the opening."
}
```

## Lifecycle protections

- Draft creation always starts in `draft`; clients cannot assign workflow status.
- Draft updates cannot change workflow status.
- Only drafts in `draft` status can be edited.
- Only drafts in `draft` status can be submitted.
- Duplicate submissions and decisions on non-pending approvals return HTTP 409.
- Approved, pending, scheduled, and published drafts cannot be deleted through the draft API.
- Rejection and requested changes return the draft to editable `draft` status. The approval record retains the most recent decision and feedback.
- Publishing integration must require `ContentDraft.status == "approved"`. This is enforced when the publishing service and endpoint are implemented; no publishing endpoint is introduced in this phase.

## Data migration

No database migration is required. The existing `approvals` table and its one-to-one relationship with content drafts support this workflow.

## Verification

Run:

```bash
docker compose up --build -d
docker compose exec backend pytest -v
docker compose exec backend ruff check --no-cache .
```
