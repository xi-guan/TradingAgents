"""股票筛选 Schemas"""

from decimal import Decimal
from pydantic import BaseModel, Field


class ScreenerCondition(BaseModel):
    """筛选条件"""

    field: str = Field(..., description="字段名称")
    operator: str = Field(..., pattern="^(gt|gte|lt|lte|eq|ne|between|in)$", description="运算符")
    value: Decimal | int | float | str | list | None = Field(..., description="比较值")


class ScreenerRequest(BaseModel):
    """筛选请求"""

    market: str = Field(..., pattern="^(CN|HK|US|ALL)$", description="市场")
    conditions: list[ScreenerCondition] = Field(default=[], description="筛选条件列表")
    order_by: str | None = Field(None, description="排序字段")
    order_direction: str = Field(default="desc", pattern="^(asc|desc)$", description="排序方向")
    limit: int = Field(default=50, ge=1, le=500, description="返回数量")
    offset: int = Field(default=0, ge=0, description="偏移量")


class ScreenerResult(BaseModel):
    """筛选结果"""

    symbol: str
    name: str
    market: str

    # 价格信息
    current_price: Decimal | None = None
    change_percent: Decimal | None = None
    volume: int | None = None
    market_cap: Decimal | None = None

    # 财务指标
    pe_ratio: Decimal | None = None
    pb_ratio: Decimal | None = None
    roe: Decimal | None = None
    roa: Decimal | None = None
    gross_margin: Decimal | None = None
    net_margin: Decimal | None = None
    revenue_growth: Decimal | None = None
    debt_to_equity: Decimal | None = None

    # 技术指标
    rsi: Decimal | None = None
    macd_signal: str | None = None

    model_config = {"from_attributes": True}


class ScreenerResponse(BaseModel):
    """筛选响应"""

    total: int
    results: list[ScreenerResult]
    conditions: list[ScreenerCondition]
