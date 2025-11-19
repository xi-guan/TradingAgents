"""股票模型"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4
from sqlalchemy import String, DateTime, Numeric, BigInteger, Index, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class Stock(Base):
    """股票基本信息"""

    __tablename__ = "stocks"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    market: Mapped[str] = mapped_column(String(10), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    sector: Mapped[str | None] = mapped_column(String(100))
    industry: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column()

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
        Index("ix_stocks_symbol_market", "symbol", "market", unique=True),
        Index("ix_stocks_market", "market"),
    )

    def __repr__(self) -> str:
        return f"<Stock {self.symbol} ({self.market}) {self.name}>"


class StockQuote(Base):
    """股票实时行情"""

    __tablename__ = "stock_quotes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    stock_id: Mapped[UUID] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    open: Mapped[Decimal | None] = mapped_column(Numeric(20, 4))
    high: Mapped[Decimal | None] = mapped_column(Numeric(20, 4))
    low: Mapped[Decimal | None] = mapped_column(Numeric(20, 4))
    close: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False)
    volume: Mapped[int | None] = mapped_column(BigInteger)
    prev_close: Mapped[Decimal | None] = mapped_column(Numeric(20, 4))
    change: Mapped[Decimal | None] = mapped_column(Numeric(20, 4))
    change_percent: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))

    # Additional field for screener (calculated field)
    market_cap: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    __table_args__ = (
        Index("ix_stock_quotes_stock_id", "stock_id"),
        Index("ix_stock_quotes_timestamp", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<StockQuote {self.stock_id} {self.close}>"


class StockHistory(Base):
    """股票历史数据（TimescaleDB 超表）"""

    __tablename__ = "stock_history"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    stock_id: Mapped[UUID] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    open: Mapped[Decimal | None] = mapped_column(Numeric(20, 4))
    high: Mapped[Decimal | None] = mapped_column(Numeric(20, 4))
    low: Mapped[Decimal | None] = mapped_column(Numeric(20, 4))
    close: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False)
    volume: Mapped[int | None] = mapped_column(BigInteger)
    adj_close: Mapped[Decimal | None] = mapped_column(Numeric(20, 4))
    interval: Mapped[str] = mapped_column(String(10), server_default="1d", nullable=False)

    __table_args__ = (
        Index("ix_stock_history_stock_timestamp", "stock_id", "timestamp", "interval", unique=True),
        Index("ix_stock_history_timestamp", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<StockHistory {self.stock_id} {self.timestamp}>"
