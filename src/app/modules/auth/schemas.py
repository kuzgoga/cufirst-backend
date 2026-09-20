from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.modules.auth.models import UserRole


class UserIn(BaseModel):
    email: EmailStr
    name: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=4, max_length=1024)


class SignInIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=4, max_length=1024)


class UserUpdateIn(BaseModel):
    name: str = Field(min_length=3, max_length=80)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    name: str
    role: UserRole
    created_at: datetime


class JwtTokenOut(BaseModel):
    accessToken: str = Field(description="JWT access token")
