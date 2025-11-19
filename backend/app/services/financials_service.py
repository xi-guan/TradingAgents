"""财务数据服务"""

import asyncio
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import httpx
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.financials import FinancialStatement, FinancialMetrics


class FinancialsService:
    """财务数据服务"""

    @staticmethod
    async def fetch_financials_yfinance(
        symbol: str, statement_type: str = "income"
    ) -> list[dict[str, Any]]:
        """从 YFinance 获取财务数据（通过 yfinance 库）"""
        try:
            import yfinance as yf

            # 在线程池中运行同步代码
            def _fetch():
                ticker = yf.Ticker(symbol)

                if statement_type == "income":
                    df = ticker.income_stmt  # 年度利润表
                elif statement_type == "balance":
                    df = ticker.balance_sheet  # 年度资产负债表
                elif statement_type == "cashflow":
                    df = ticker.cashflow  # 年度现金流量表
                else:
                    return []

                if df is None or df.empty:
                    return []

                statements = []
                for col in df.columns:
                    # 解析日期
                    report_date = col.date() if hasattr(col, "date") else col

                    statement_data = {
                        "statement_type": statement_type,
                        "period_type": "annual",
                        "fiscal_year": report_date.year,
                        "fiscal_quarter": None,
                        "report_date": report_date,
                        "currency": "USD",
                        "source": "YFinance",
                    }

                    # 提取数据（YFinance 字段名可能不同，需要映射）
                    if statement_type == "income":
                        statement_data.update(
                            {
                                "revenue": _safe_decimal(df.loc["Total Revenue", col])
                                if "Total Revenue" in df.index
                                else None,
                                "cost_of_revenue": _safe_decimal(df.loc["Cost Of Revenue", col])
                                if "Cost Of Revenue" in df.index
                                else None,
                                "gross_profit": _safe_decimal(df.loc["Gross Profit", col])
                                if "Gross Profit" in df.index
                                else None,
                                "operating_income": _safe_decimal(df.loc["Operating Income", col])
                                if "Operating Income" in df.index
                                else None,
                                "net_income": _safe_decimal(df.loc["Net Income", col])
                                if "Net Income" in df.index
                                else None,
                                "ebitda": _safe_decimal(df.loc["EBITDA", col])
                                if "EBITDA" in df.index
                                else None,
                            }
                        )
                    elif statement_type == "balance":
                        statement_data.update(
                            {
                                "total_assets": _safe_decimal(df.loc["Total Assets", col])
                                if "Total Assets" in df.index
                                else None,
                                "total_liabilities": _safe_decimal(
                                    df.loc["Total Liabilities Net Minority Interest", col]
                                )
                                if "Total Liabilities Net Minority Interest" in df.index
                                else None,
                                "total_equity": _safe_decimal(df.loc["Stockholders Equity", col])
                                if "Stockholders Equity" in df.index
                                else None,
                                "current_assets": _safe_decimal(df.loc["Current Assets", col])
                                if "Current Assets" in df.index
                                else None,
                                "current_liabilities": _safe_decimal(
                                    df.loc["Current Liabilities", col]
                                )
                                if "Current Liabilities" in df.index
                                else None,
                                "cash_and_equivalents": _safe_decimal(
                                    df.loc["Cash And Cash Equivalents", col]
                                )
                                if "Cash And Cash Equivalents" in df.index
                                else None,
                            }
                        )
                    elif statement_type == "cashflow":
                        statement_data.update(
                            {
                                "operating_cashflow": _safe_decimal(
                                    df.loc["Operating Cash Flow", col]
                                )
                                if "Operating Cash Flow" in df.index
                                else None,
                                "investing_cashflow": _safe_decimal(
                                    df.loc["Investing Cash Flow", col]
                                )
                                if "Investing Cash Flow" in df.index
                                else None,
                                "financing_cashflow": _safe_decimal(
                                    df.loc["Financing Cash Flow", col]
                                )
                                if "Financing Cash Flow" in df.index
                                else None,
                                "free_cashflow": _safe_decimal(df.loc["Free Cash Flow", col])
                                if "Free Cash Flow" in df.index
                                else None,
                            }
                        )

                    statements.append(statement_data)

                return statements

            def _safe_decimal(value):
                """安全转换为 Decimal"""
                if value is None or (hasattr(value, "isna") and value.isna()):
                    return None
                try:
                    return Decimal(str(float(value)))
                except (ValueError, TypeError):
                    return None

            # 在线程池中运行
            statements = await asyncio.to_thread(_fetch)
            return statements

        except Exception as e:
            print(f"Error fetching financials from YFinance: {e}")
            return []

    @staticmethod
    async def save_financial_statement(
        db: AsyncSession, symbol: str, market: str, statement_data: dict[str, Any]
    ) -> FinancialStatement | None:
        """保存财务报表（去重）"""
        # 检查是否已存在
        stmt = select(FinancialStatement).where(
            and_(
                FinancialStatement.symbol == symbol,
                FinancialStatement.market == market,
                FinancialStatement.statement_type == statement_data["statement_type"],
                FinancialStatement.period_type == statement_data["period_type"],
                FinancialStatement.fiscal_year == statement_data["fiscal_year"],
                FinancialStatement.fiscal_quarter == statement_data.get("fiscal_quarter"),
            )
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            return existing

        # 创建新记录
        statement = FinancialStatement(symbol=symbol, market=market, **statement_data)

        db.add(statement)
        await db.commit()
        await db.refresh(statement)

        return statement

    @staticmethod
    async def get_financial_statements(
        db: AsyncSession,
        symbol: str,
        market: str,
        statement_type: str | None = None,
        period_type: str | None = None,
        limit: int = 5,
        fetch_if_empty: bool = True,
    ) -> list[FinancialStatement]:
        """获取财务报表"""
        # 构建查询
        conditions = [
            FinancialStatement.symbol == symbol,
            FinancialStatement.market == market,
        ]

        if statement_type:
            conditions.append(FinancialStatement.statement_type == statement_type)
        if period_type:
            conditions.append(FinancialStatement.period_type == period_type)

        stmt = (
            select(FinancialStatement)
            .where(and_(*conditions))
            .order_by(desc(FinancialStatement.report_date))
            .limit(limit)
        )

        result = await db.execute(stmt)
        statements = list(result.scalars().all())

        # 如果为空且允许获取，则从 API 获取
        if not statements and fetch_if_empty and statement_type:
            fetched = await FinancialsService.fetch_financials_yfinance(
                symbol, statement_type
            )
            for data in fetched[:limit]:
                stmt = await FinancialsService.save_financial_statement(
                    db, symbol, market, data
                )
                if stmt:
                    statements.append(stmt)

        return statements

    @staticmethod
    async def calculate_financial_metrics(
        db: AsyncSession, symbol: str, market: str, report_date: date
    ) -> FinancialMetrics | None:
        """计算财务指标"""
        # 获取对应日期的财务报表
        year = report_date.year

        # 获取利润表
        income_stmt = (
            select(FinancialStatement)
            .where(
                and_(
                    FinancialStatement.symbol == symbol,
                    FinancialStatement.market == market,
                    FinancialStatement.statement_type == "income",
                    FinancialStatement.fiscal_year == year,
                )
            )
            .limit(1)
        )
        result = await db.execute(income_stmt)
        income = result.scalar_one_or_none()

        # 获取资产负债表
        balance_stmt = (
            select(FinancialStatement)
            .where(
                and_(
                    FinancialStatement.symbol == symbol,
                    FinancialStatement.market == market,
                    FinancialStatement.statement_type == "balance",
                    FinancialStatement.fiscal_year == year,
                )
            )
            .limit(1)
        )
        result = await db.execute(balance_stmt)
        balance = result.scalar_one_or_none()

        if not income or not balance:
            return None

        # 计算指标
        metrics_data = {
            "symbol": symbol,
            "market": market,
            "report_date": report_date,
            "period_type": "annual",
            "source": "calculated",
        }

        # 盈利能力
        if balance.total_equity and income.net_income:
            metrics_data["roe"] = income.net_income / balance.total_equity

        if balance.total_assets and income.net_income:
            metrics_data["roa"] = income.net_income / balance.total_assets

        if income.revenue and income.gross_profit:
            metrics_data["gross_margin"] = income.gross_profit / income.revenue

        if income.revenue and income.operating_income:
            metrics_data["operating_margin"] = income.operating_income / income.revenue

        if income.revenue and income.net_income:
            metrics_data["net_margin"] = income.net_income / income.revenue

        # 偿债能力
        if balance.current_assets and balance.current_liabilities:
            metrics_data["current_ratio"] = (
                balance.current_assets / balance.current_liabilities
            )

        if balance.total_liabilities and balance.total_equity:
            metrics_data["debt_to_equity"] = (
                balance.total_liabilities / balance.total_equity
            )

        # 检查是否已存在
        stmt = select(FinancialMetrics).where(
            and_(
                FinancialMetrics.symbol == symbol,
                FinancialMetrics.market == market,
                FinancialMetrics.report_date == report_date,
            )
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            return existing

        # 创建新记录
        metrics = FinancialMetrics(**metrics_data)
        db.add(metrics)
        await db.commit()
        await db.refresh(metrics)

        return metrics

    @staticmethod
    async def get_financial_metrics(
        db: AsyncSession, symbol: str, market: str, limit: int = 5
    ) -> list[FinancialMetrics]:
        """获取财务指标"""
        stmt = (
            select(FinancialMetrics)
            .where(
                and_(
                    FinancialMetrics.symbol == symbol,
                    FinancialMetrics.market == market,
                )
            )
            .order_by(desc(FinancialMetrics.report_date))
            .limit(limit)
        )

        result = await db.execute(stmt)
        return list(result.scalars().all())
