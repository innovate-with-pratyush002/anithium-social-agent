from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_admin
from app.db.session import get_db_session
from app.models.social_account import SocialAccount
from app.models.user import User
from app.schemas.social_account import SocialAccountRead

router = APIRouter(
    prefix="/social-accounts",
    tags=["Social Accounts"],
    dependencies=[Depends(require_admin)],
)


@router.get("", response_model=list[SocialAccountRead])
async def list_social_accounts(
    current_user: Annotated[User, Depends(require_admin)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[SocialAccount]:
    result = await session.scalars(
        select(SocialAccount)
        .where(SocialAccount.user_id == current_user.id)
        .order_by(SocialAccount.platform, SocialAccount.account_name)
    )
    return list(result.all())


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def disconnect_social_account(
    account_id: UUID,
    current_user: Annotated[User, Depends(require_admin)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    account = await session.scalar(
        select(SocialAccount)
        .where(
            SocialAccount.id == account_id,
            SocialAccount.user_id == current_user.id,
        )
        .with_for_update()
    )
    if account is None:
        raise HTTPException(status_code=404, detail="Social account not found.")
    account.is_active = False
    account.access_token_encrypted = "REVOKED"
    account.refresh_token_encrypted = None
    await session.commit()
