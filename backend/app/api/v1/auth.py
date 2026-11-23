from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.config import get_settings
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserRead

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> User:
    email = payload.email.strip().lower()
    existing = await session.scalar(select(User).where(func.lower(User.email) == email))
    if existing is not None:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    user = User(
        email=email,
        full_name=payload.full_name.strip(),
        password_hash=hash_password(payload.password),
        is_active=True,
        is_admin=False,
    )
    session.add(user)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists.") from exc
    await session.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TokenResponse:
    email = payload.email.strip().lower()
    user = await session.scalar(select(User).where(func.lower(User.email) == email))
    if (
        user is None
        or user.password_hash is None
        or not verify_password(payload.password, user.password_hash)
        or not user.is_active
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user.last_login_at = datetime.now(UTC)
    await session.commit()
    return TokenResponse(
        access_token=create_access_token(user.id),
        expires_in=get_settings().access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=UserRead)
async def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user
