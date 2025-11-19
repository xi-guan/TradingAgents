"""财务数据模型"""

from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Date, DateTime, String, Numeric, Integer, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class FinancialStatement(Base):
    """财务报表（利润表、资产负债表、现金流量表）"""

    __tablename__ = "financial_statements"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # 关联股票
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    market: Mapped[str] = mapped_column(String(10), index=True)

    # 报表类型和周期
    statement_type: Mapped[str] = mapped_column(String(20))  # income, balance, cashflow
    period_type: Mapped[str] = mapped_column(String(20))  # annual, quarterly
    fiscal_year: Mapped[int] = mapped_column(Integer)
    fiscal_quarter: Mapped[int | None] = mapped_column(Integer)  # 1, 2, 3, 4
    report_date: Mapped[date] = mapped_column(Date, index=True)

    # 利润表 (Income Statement)
    revenue: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))  # 营业收入
    cost_of_revenue: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))  # 营业成本
    gross_profit: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))  # 毛利润
    operating_expenses: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))  # 营业费用
    operating_income: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))  # 营业利润
    net_income: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))  # 净利润
    ebitda: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))  # EBITDA
    eps: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))  # 每股收益

    # 资产负债表 (Balance Sheet)
    total_assets: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))  # 总资产
    total_liabilities: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))  # 总负债
    total_equity: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))  # 股东权益
    current_assets: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))  # 流动资产
    current_liabilities: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))  # 流动负债
    cash_and_equivalents: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))  # 现金及等价物

    # 现金流量表 (Cash Flow Statement)
    operating_cashflow: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))  # 经营现金流
    investing_cashflow: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))  # 投资现金流
    financing_cashflow: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))  # 筹资现金流
    free_cashflow: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))  # 自由现金流

    # 元数据
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    source: Mapped[str] = mapped_column(String(50))  # 数据来源
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
        # 唯一约束：同一股票、同一报表类型、同一周期只能有一条记录
        Index(
            "ix_financial_unique",
            "symbol",
            "market",
            "statement_type",
            "period_type",
            "fiscal_year",
            "fiscal_quarter",
            unique=True,
        ),
        # 按股票和日期查询
        Index("ix_financial_symbol_date", "symbol", "market", "report_date"),
    )

    def __repr__(self) -> str:
        return f"<FinancialStatement {self.symbol} {self.statement_type} {self.fiscal_year}Q{self.fiscal_quarter or 'Y'}>"


class FinancialMetrics(Base):
    """财务指标（计算得出的比率和指标）"""

    __tablename__ = "financial_metrics"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # 关联股票
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    market: Mapped[str] = mapped_column(String(10), index=True)

    # 时间周期
    report_date: Mapped[date] = mapped_column(Date, index=True)
    period_type: Mapped[str] = mapped_column(String(20))  # annual, quarterly, ttm

    # 估值指标
    pe_ratio: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))  # 市盈率
    pb_ratio: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))  # 市净率
    ps_ratio: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))  # 市销率
    pcf_ratio: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))  # 市现率
    ev_to_ebitda: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))  # EV/EBITDA

    # 盈利能力
    roe: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))  # 净资产收益率
    roa: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))  # 总资产收益率
    gross_margin: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))  # 毛利率
    operating_margin: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))  # 营业利润率
    net_margin: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))  # 净利率

    # 成长性
    revenue_growth: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))  # 营收增长率
    earnings_growth: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))  # 利润增长率

    # 偿债能力
    current_ratio: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))  # 流动比率
    quick_ratio: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))  # 速动比率
    debt_to_equity: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))  # 资产负债率

    # 运营效率
    asset_turnover: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))  # 总资产周转率
    inventory_turnover: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))  # 存货周转率

    # 元数据
    source: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    __table_args__ = (
        Index(
            "ix_metrics_unique",
            "symbol",
            "market",
            "report_date",
            "period_type",
            unique=True,
        ),
        Index("ix_metrics_symbol_date", "symbol", "market", "report_date"),
    )

    def __repr__(self) -> str:
        return f"<FinancialMetrics {self.symbol} {self.report_date}>"
