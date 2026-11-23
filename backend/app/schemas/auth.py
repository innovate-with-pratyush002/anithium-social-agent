from uuid import UUID

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    email: str = Field(min_length=5, max_length=320)
    full_name: str = Field(min_length=1, max_length=160)
    password: str = Field(min_length=12, max_length=128)


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=320)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserRead(BaseModel):
    id: UUID
    email: str
    full_name: str
    is_active: bool
    is_admin: bool
