from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field, model_validator

from app.schemas.common import ORMModel
from app.schemas.content_draft import ContentDraftRead

ApprovalStatus = Literal["pending", "approved", "rejected", "changes_requested"]
ApprovalDecision = Literal["approved", "rejected", "changes_requested"]


class ApprovalDecisionRequest(ORMModel):
    decision: ApprovalDecision
    feedback: str | None = Field(default=None, max_length=5000)

    @model_validator(mode="after")
    def require_feedback_for_non_approval(self):
        if self.decision in {"rejected", "changes_requested"} and not (
            self.feedback and self.feedback.strip()
        ):
            raise ValueError("Feedback is required when rejecting or requesting changes.")
        return self


class ApprovalRead(ORMModel):
    id: UUID
    content_draft_id: UUID
    reviewer_id: UUID | None
    status: ApprovalStatus
    feedback: str | None
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    content_draft: ContentDraftRead
