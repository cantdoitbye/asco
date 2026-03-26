from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from ..models import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: Optional[UserRole] = UserRole.AWW


class UserCreate(UserBase):
    password: str
    stakeholder_id: Optional[int] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    stakeholder_id: Optional[int] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    stakeholder_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenPayload(BaseModel):
    sub: int
    exp: datetime
    email: str
    role: UserRole
