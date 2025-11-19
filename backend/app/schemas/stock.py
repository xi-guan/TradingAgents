"""股票 Schemas"""

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class StockInfo(BaseModel):
    """股票基本信息"""

    symbol: str
    market: str
    name: str
    full_symbol: str
    industry: str | None = None
    area: str | None = None
    list_date: str | None = None

    model_config = {"from_attributes": True}


class StockQuote(BaseModel):
    """股票实时行情"""

    symbol: str
    market: str
    price: Decimal
    change: Decimal
    change_percent: Decimal
    volume: int
    amount: Decimal
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    prev_close: Decimal
    timestamp: datetime

    model_config = {"from_attributes": True}


class StockHistory(BaseModel):
    """股票历史数据"""

    time: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    amount: Decimal | None = None

    model_config = {"from_attributes": True}


class StockSearch(BaseModel):
    """股票搜索结果"""

    symbol: str
    name: str
    market: str
    full_symbol: str
