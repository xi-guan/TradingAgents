"""分析任务模型"""

from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, DateTime, Integer, JSON, Text, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class AnalysisTask(Base):
    """股票分析任务"""

    __tablename__ = "analysis_tasks"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True)

    symbol: Mapped[str] = mapped_column(String(20))
    market: Mapped[str] = mapped_column(String(10))
    analysis_date: Mapped[str] = mapped_column(String(20))
    depth: Mapped[int] = mapped_column(Integer, default=3)

    status: Mapped[str] = mapped_column(String(20), default="pending")
    progress: Mapped[int] = mapped_column(Integer, default=0)

    result: Mapped[dict | None] = mapped_column(JSON)
    error_message: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        Index("idx_analysis_user_created", "user_id", "created_at"),
        Index("idx_analysis_status", "status", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<AnalysisTask {self.symbol} {self.status}>"
