"""自选股 Schemas"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class WatchlistItemCreate(BaseModel):
    """添加自选股"""

    symbol: str = Field(..., min_length=1, max_length=20)
    market: str = Field(..., pattern="^(CN|HK|US)$")
    group_name: str | None = Field(None, max_length=50)
    notes: str | None = Field(None, max_length=500)


class WatchlistItemUpdate(BaseModel):
    """更新自选股"""

    group_name: str | None = Field(None, max_length=50)
    notes: str | None = Field(None, max_length=500)


class WatchlistItemResponse(BaseModel):
    """自选股响应"""

    id: UUID
    user_id: UUID
    stock_id: UUID
    symbol: str
    name: str
    market: str
    group_name: str | None
    notes: str | None
    created_at: datetime

    # 实时行情数据（可选）
    current_price: float | None = None
    change: float | None = None
    change_percent: float | None = None

    model_config = {"from_attributes": True}


class WatchlistGroupResponse(BaseModel):
    """自选股分组响应"""

    group_name: str
    count: int
    stocks: list[WatchlistItemResponse]
