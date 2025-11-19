"""新闻数据模型"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, String, Text, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class NewsArticle(Base):
    """新闻文章"""

    __tablename__ = "news_articles"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # 关联股票
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    market: Mapped[str] = mapped_column(String(10), index=True)

    # 新闻内容
    title: Mapped[str] = mapped_column(String(500))
    summary: Mapped[str | None] = mapped_column(Text)
    content: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str] = mapped_column(String(1000))

    # 来源和作者
    source: Mapped[str] = mapped_column(String(100))  # Alpha Vantage, Finnhub, etc.
    author: Mapped[str | None] = mapped_column(String(200))

    # 情感分析（可选）
    sentiment: Mapped[str | None] = mapped_column(String(20))  # positive, negative, neutral
    sentiment_score: Mapped[float | None] = mapped_column()

    # 时间
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    __table_args__ = (
        # 防止重复新闻
        Index("ix_news_url_unique", "url", unique=True),
        # 按股票和时间查询
        Index("ix_news_symbol_published", "symbol", "market", "published_at"),
    )

    def __repr__(self) -> str:
        return f"<NewsArticle {self.symbol} {self.title[:50]}>"
