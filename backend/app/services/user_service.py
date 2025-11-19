"""用户服务"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class UserService:
    """用户服务"""

    @staticmethod
    async def create_user(db: AsyncSession, user_create: UserCreate) -> User:
        """创建用户"""
        # 检查用户名是否已存在
        result = await db.execute(
            select(User).where(User.username == user_create.username)
        )
        if result.scalar_one_or_none():
            raise ValueError("用户名已存在")

        # 检查邮箱是否已存在
        result = await db.execute(
            select(User).where(User.email == user_create.email)
        )
        if result.scalar_one_or_none():
            raise ValueError("邮箱已被注册")

        # 创建用户
        user = User(
            username=user_create.username,
            email=user_create.email,
            hashed_password=get_password_hash(user_create.password),
            preferred_language=user_create.preferred_language,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def authenticate(db: AsyncSession, username: str, password: str) -> User | None:
        """认证用户"""
        result = await db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
        """根据ID获取用户"""
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_user(db: AsyncSession, user: User, user_update: UserUpdate) -> User:
        """更新用户"""
        if user_update.email:
            # 检查邮箱是否已被其他用户使用
            result = await db.execute(
                select(User).where(User.email == user_update.email, User.id != user.id)
            )
            if result.scalar_one_or_none():
                raise ValueError("邮箱已被使用")
            user.email = user_update.email

        if user_update.preferred_language:
            user.preferred_language = user_update.preferred_language

        await db.commit()
        await db.refresh(user)

        return user
