"""用户股票收藏模型"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, String, func, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserStock(Base):
    """用户股票收藏/自选股"""

    __tablename__ = "user_stocks"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    stock_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)

    # 分组名称（可选，用于分类管理）
    group_name: Mapped[str | None] = mapped_column(String(50))

    # 备注（可选）
    notes: Mapped[str | None] = mapped_column(String(500))

    # 添加时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    __table_args__ = (
        # 确保同一个用户不会重复收藏同一只股票
        UniqueConstraint("user_id", "stock_id", name="uq_user_stock"),
        # 索引：方便按用户和分组查询
        Index("ix_user_stock_user_group", "user_id", "group_name"),
    )

    def __repr__(self) -> str:
        return f"<UserStock user={self.user_id} stock={self.stock_id}>"
