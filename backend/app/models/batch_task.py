"""批量分析任务模型"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, String, Integer, Text, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class BatchAnalysisTask(Base):
    """批量分析任务"""

    __tablename__ = "batch_analysis_tasks"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)

    # 任务名称
    name: Mapped[str] = mapped_column(String(200))

    # 批量参数（JSON 格式）
    # 例如: {"symbols": ["AAPL", "GOOGL"], "markets": ["US", "US"], "depth": 3}
    parameters: Mapped[dict] = mapped_column(JSON)

    # 任务状态: pending, running, completed, failed, cancelled
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)

    # 进度统计
    total_count: Mapped[int] = mapped_column(Integer, default=0)
    completed_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)

    # 子任务 ID 列表
    subtask_ids: Mapped[list | None] = mapped_column(JSON)

    # 错误信息
    error: Mapped[str | None] = mapped_column(Text)

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    def __repr__(self) -> str:
        return f"<BatchAnalysisTask {self.name} {self.status}>"
