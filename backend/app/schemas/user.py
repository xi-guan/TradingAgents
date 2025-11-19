"""用户 Schemas"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID


class UserCreate(BaseModel):
    """用户注册"""

    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    preferred_language: str = Field(default="zh_CN", pattern="^(zh_CN|en_US)$")


class UserLogin(BaseModel):
    """用户登录"""

    username: str
    password: str


class UserResponse(BaseModel):
    """用户响应"""

    id: UUID
    username: str
    email: str
    is_active: bool
    is_verified: bool
    preferred_language: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """用户更新"""

    email: EmailStr | None = None
    preferred_language: str | None = Field(None, pattern="^(zh_CN|en_US)$")


class Token(BaseModel):
    """JWT Token"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
