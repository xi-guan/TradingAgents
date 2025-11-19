"""交易模型"""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4
from sqlalchemy import String, DateTime, Integer, Numeric, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class TradingAccount(Base):
    """模拟交易账户"""

    __tablename__ = "trading_accounts"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), unique=True, index=True)
    account_type: Mapped[str] = mapped_column(String(20), default="paper")

    # 多货币账户
    cash_cny: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=Decimal("1000000"))
    cash_hkd: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=Decimal("1000000"))
    cash_usd: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=Decimal("100000"))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<TradingAccount {self.user_id}>"


class Position(Base):
    """持仓"""

    __tablename__ = "positions"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    account_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True)

    symbol: Mapped[str] = mapped_column(String(20))
    market: Mapped[str] = mapped_column(String(10))
    quantity: Mapped[int] = mapped_column(Integer)
    avg_cost: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    current_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    unrealized_pnl: Mapped[Decimal | None] = mapped_column(Numeric(20, 4))

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
        Index("idx_position_account_symbol", "account_id", "symbol", "market"),
    )

    def __repr__(self) -> str:
        return f"<Position {self.symbol} x{self.quantity}>"


class Order(Base):
    """订单"""

    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    account_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True)

    symbol: Mapped[str] = mapped_column(String(20))
    market: Mapped[str] = mapped_column(String(10))
    side: Mapped[str] = mapped_column(String(10))  # buy, sell
    order_type: Mapped[str] = mapped_column(String(10))  # market, limit

    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    filled_quantity: Mapped[int] = mapped_column(Integer, default=0)
    filled_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))

    status: Mapped[str] = mapped_column(String(20), default="pending")
    filled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    __table_args__ = (
        Index("idx_order_account_created", "account_id", "created_at"),
        Index("idx_order_status", "status", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Order {self.side} {self.symbol} x{self.quantity}>"
