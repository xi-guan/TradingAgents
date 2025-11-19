"""新闻数据 Schemas"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class NewsArticleResponse(BaseModel):
    """新闻文章响应"""

    id: UUID
    symbol: str
    market: str
    title: str
    summary: str | None
    content: str | None
    url: str
    source: str
    author: str | None
    sentiment: str | None
    sentiment_score: float | None
    published_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class NewsQuery(BaseModel):
    """新闻查询参数"""

    symbol: str = Field(..., min_length=1, max_length=20)
    market: str = Field(..., pattern="^(CN|HK|US)$")
    limit: int = Field(default=10, ge=1, le=100)
    from_date: datetime | None = None
    to_date: datetime | None = None
