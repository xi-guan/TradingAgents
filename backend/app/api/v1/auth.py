"""认证 API"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services.user_service import UserService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_create: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """用户注册"""
    try:
        user = await UserService.create_user(db, user_create)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=Token)
async def login(
    user_login: UserLogin,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """用户登录"""
    user = await UserService.authenticate(db, user_login.username, user_login.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )

    # 创建令牌
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=dict)
async def refresh_token(
    refresh_token: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """刷新令牌"""
    # 解码刷新令牌
    payload = decode_token(refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌",
        )

    # 检查令牌类型
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌类型",
        )

    # 获取用户ID
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌",
        )

    # 验证用户是否存在
    user = await UserService.get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用",
        )

    # 创建新的访问令牌
    new_access_token = create_access_token({"sub": str(user.id)})

    return {"access_token": new_access_token}
