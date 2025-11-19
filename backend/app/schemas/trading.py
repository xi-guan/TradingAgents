"""交易 Schemas"""

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from uuid import UUID


class TradingAccountCreate(BaseModel):
    """创建交易账户"""

    account_type: str = Field(default="paper", pattern="^(paper|live)$")
    market: str = Field(default="CN", pattern="^(CN|HK|US)$")
    initial_cash: Decimal = Field(default=Decimal("1000000"), gt=0)


class TradingAccountResponse(BaseModel):
    """交易账户响应"""

    id: UUID
    user_id: UUID
    account_type: str
    cash_cny: Decimal
    cash_hkd: Decimal
    cash_usd: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PositionResponse(BaseModel):
    """持仓响应"""

    id: UUID
    account_id: UUID
    symbol: str
    market: str
    quantity: int
    avg_cost: Decimal
    current_price: Decimal | None
    unrealized_pnl: Decimal | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    """创建订单"""

    symbol: str = Field(..., min_length=1, max_length=20)
    market: str = Field(..., pattern="^(CN|HK|US)$")
    side: str = Field(..., pattern="^(buy|sell)$")
    order_type: str = Field(..., pattern="^(market|limit)$")
    quantity: int = Field(..., gt=0)
    price: Decimal | None = Field(None, gt=0)


class OrderResponse(BaseModel):
    """订单响应"""

    id: UUID
    account_id: UUID
    symbol: str
    market: str
    side: str
    order_type: str
    quantity: int
    price: Decimal | None
    filled_quantity: int
    filled_price: Decimal | None
    status: str
    filled_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
