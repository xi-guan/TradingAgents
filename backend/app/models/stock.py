"""股票模型"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, DateTime, Numeric, BigInteger, Index, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class Stock(Base):
    """股票基本信息"""

    __tablename__ = "stocks"

    symbol: Mapped[str] = mapped_column(String(20), primary_key=True)
    market: Mapped[str] = mapped_column(String(10), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    full_symbol: Mapped[str] = mapped_column(String(30), index=True)
    industry: Mapped[str | None] = mapped_column(String(100))
    area: Mapped[str | None] = mapped_column(String(100))
    list_date: Mapped[str | None] = mapped_column(String(20))

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
        Index("idx_stock_full_symbol", "full_symbol"),
    )

    def __repr__(self) -> str:
        return f"<Stock {self.full_symbol} {self.name}>"


class StockQuote(Base):
    """股票实时行情"""

    __tablename__ = "stock_quotes"

    symbol: Mapped[str] = mapped_column(String(20), primary_key=True)
    market: Mapped[str] = mapped_column(String(10), primary_key=True)

    price: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    change: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    change_percent: Mapped[Decimal] = mapped_column(Numeric(8, 4))
    volume: Mapped[int] = mapped_column(BigInteger)
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 4))

    open: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    high: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    low: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    close: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    prev_close: Mapped[Decimal] = mapped_column(Numeric(12, 4))

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<StockQuote {self.symbol} {self.price}>"


class StockHistory(Base):
    """股票历史数据（TimescaleDB 超表）"""

    __tablename__ = "stock_history"

    time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        primary_key=True,
    )
    symbol: Mapped[str] = mapped_column(String(20), primary_key=True)
    market: Mapped[str] = mapped_column(String(10), primary_key=True)

    open: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    high: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    low: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    close: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    volume: Mapped[int] = mapped_column(BigInteger)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(20, 4))

    __table_args__ = (
        Index("idx_stock_history_symbol_market", "symbol", "market", "time"),
    )

    def __repr__(self) -> str:
        return f"<StockHistory {self.symbol} {self.time}>"
