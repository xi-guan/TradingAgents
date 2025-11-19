"""用户 API"""

from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies import CurrentUser
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUser):
    """获取当前用户信息"""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """更新当前用户信息"""
    try:
        updated_user = await UserService.update_user(db, current_user, user_update)
        return updated_user
    except ValueError as e:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
