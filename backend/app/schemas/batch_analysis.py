"""批量分析 Schemas"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BatchAnalysisCreate(BaseModel):
    """创建批量分析任务"""

    name: str = Field(..., min_length=1, max_length=200)
    symbols: list[str] = Field(..., min_length=1, max_length=50)
    markets: list[str] = Field(..., min_length=1, max_length=50)
    depth: int = Field(default=3, ge=1, le=5)

    # 可选：从自选股分组批量分析
    from_watchlist_group: str | None = None


class BatchAnalysisResponse(BaseModel):
    """批量分析任务响应"""

    id: UUID
    user_id: UUID
    name: str
    parameters: dict
    status: str
    total_count: int
    completed_count: int
    failed_count: int
    subtask_ids: list[UUID] | None
    error: str | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None

    # 计算属性
    progress_percent: float | None = None

    model_config = {"from_attributes": True}


class BatchAnalysisProgress(BaseModel):
    """批量分析进度"""

    task_id: UUID
    status: str
    total_count: int
    completed_count: int
    failed_count: int
    progress_percent: float
    current_symbol: str | None = None
