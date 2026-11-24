from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SocialAccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    platform: str
    external_account_id: str
    account_name: str | None
    account_type: str | None
    token_expires_at: datetime | None
    granted_scopes: list[str]
    is_active: bool
    connected_at: datetime
