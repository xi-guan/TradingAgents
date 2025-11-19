"""财务数据 Schemas"""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class FinancialStatementResponse(BaseModel):
    """财务报表响应"""

    id: UUID
    symbol: str
    market: str
    statement_type: str
    period_type: str
    fiscal_year: int
    fiscal_quarter: int | None
    report_date: date

    # 利润表
    revenue: Decimal | None
    cost_of_revenue: Decimal | None
    gross_profit: Decimal | None
    operating_expenses: Decimal | None
    operating_income: Decimal | None
    net_income: Decimal | None
    ebitda: Decimal | None
    eps: Decimal | None

    # 资产负债表
    total_assets: Decimal | None
    total_liabilities: Decimal | None
    total_equity: Decimal | None
    current_assets: Decimal | None
    current_liabilities: Decimal | None
    cash_and_equivalents: Decimal | None

    # 现金流量表
    operating_cashflow: Decimal | None
    investing_cashflow: Decimal | None
    financing_cashflow: Decimal | None
    free_cashflow: Decimal | None

    currency: str
    source: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FinancialMetricsResponse(BaseModel):
    """财务指标响应"""

    id: UUID
    symbol: str
    market: str
    report_date: date
    period_type: str

    # 估值指标
    pe_ratio: Decimal | None
    pb_ratio: Decimal | None
    ps_ratio: Decimal | None
    pcf_ratio: Decimal | None
    ev_to_ebitda: Decimal | None

    # 盈利能力
    roe: Decimal | None
    roa: Decimal | None
    gross_margin: Decimal | None
    operating_margin: Decimal | None
    net_margin: Decimal | None

    # 成长性
    revenue_growth: Decimal | None
    earnings_growth: Decimal | None

    # 偿债能力
    current_ratio: Decimal | None
    quick_ratio: Decimal | None
    debt_to_equity: Decimal | None

    # 运营效率
    asset_turnover: Decimal | None
    inventory_turnover: Decimal | None

    source: str
    created_at: datetime

    model_config = {"from_attributes": True}


class FinancialQuery(BaseModel):
    """财务数据查询参数"""

    symbol: str = Field(..., min_length=1, max_length=20)
    market: str = Field(..., pattern="^(CN|HK|US)$")
    statement_type: str | None = Field(None, pattern="^(income|balance|cashflow)$")
    period_type: str | None = Field(None, pattern="^(annual|quarterly)$")
    limit: int = Field(default=5, ge=1, le=20)
