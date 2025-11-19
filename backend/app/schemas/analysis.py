"""分析 Schemas"""

from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class AnalysisTaskCreate(BaseModel):
    """创建分析任务"""

    symbol: str = Field(..., min_length=1, max_length=20)
    market: str = Field(..., pattern="^(CN|HK|US)$")
    analysis_date: str | None = None
    depth: int = Field(default=3, ge=1, le=5)


class AnalysisResult(BaseModel):
    """分析结果"""

    symbol: str
    market: str
    fundamental: dict | None = None
    technical: dict | None = None
    sentiment: dict | None = None
    news: dict | None = None
    recommendation: dict
    risk_assessment: dict


class AnalysisTaskResponse(BaseModel):
    """分析任务响应"""

    id: UUID
    user_id: UUID
    symbol: str
    market: str
    analysis_date: str
    depth: int
    status: str
    progress: int
    result: dict | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AnalysisProgress(BaseModel):
    """分析进度"""

    task_id: str
    progress: int
    stage: str
    message: str
    timestamp: datetime
