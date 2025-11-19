"""财务数据 API 路由"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.financials import FinancialStatementResponse, FinancialMetricsResponse
from app.services.financials_service import FinancialsService

router = APIRouter()


@router.get("/{symbol}/statements", response_model=list[FinancialStatementResponse])
async def get_financial_statements(
    symbol: str,
    market: str = Query(..., pattern="^(CN|HK|US)$"),
    statement_type: str | None = Query(None, pattern="^(income|balance|cashflow)$"),
    period_type: str | None = Query(None, pattern="^(annual|quarterly)$"),
    limit: int = Query(default=5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """
    获取财务报表

    Parameters:
        - symbol: 股票代码
        - market: 市场 (CN, HK, US)
        - statement_type: 报表类型 (income=利润表, balance=资产负债表, cashflow=现金流量表)
        - period_type: 周期类型 (annual=年报, quarterly=季报)
        - limit: 返回数量（默认 5）

    Returns:
        财务报表列表，按日期倒序
    """
    return await FinancialsService.get_financial_statements(
        db, symbol, market, statement_type, period_type, limit
    )


@router.get("/{symbol}/metrics", response_model=list[FinancialMetricsResponse])
async def get_financial_metrics(
    symbol: str,
    market: str = Query(..., pattern="^(CN|HK|US)$"),
    limit: int = Query(default=5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """
    获取财务指标

    Parameters:
        - symbol: 股票代码
        - market: 市场 (CN, HK, US)
        - limit: 返回数量（默认 5）

    Returns:
        财务指标列表，包括估值、盈利能力、偿债能力等
    """
    return await FinancialsService.get_financial_metrics(db, symbol, market, limit)


@router.post("/{symbol}/statements/refresh", response_model=list[FinancialStatementResponse])
async def refresh_financial_statements(
    symbol: str,
    market: str = Query(..., pattern="^(CN|HK|US)$"),
    statement_type: str = Query(..., pattern="^(income|balance|cashflow)$"),
    db: AsyncSession = Depends(get_db),
):
    """
    强制刷新财务报表（从 API 获取最新数据）

    Parameters:
        - symbol: 股票代码
        - market: 市场 (CN, HK, US)
        - statement_type: 报表类型

    Returns:
        财务报表列表
    """
    # 从 API 获取
    statements_data = await FinancialsService.fetch_financials_yfinance(
        symbol, statement_type
    )

    # 保存到数据库
    statements = []
    for data in statements_data[:5]:
        stmt = await FinancialsService.save_financial_statement(
            db, symbol, market, data
        )
        if stmt:
            statements.append(stmt)

    return statements
