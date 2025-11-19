"""股票筛选服务"""

from decimal import Decimal
from typing import Any

from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stock import Stock, StockQuote
from app.models.financials import FinancialMetrics
from app.schemas.screener import ScreenerCondition, ScreenerRequest


class ScreenerService:
    """股票筛选服务"""

    # 字段映射 (前端字段名 -> 数据库字段)
    FIELD_MAPPING = {
        # 基本信息
        "symbol": Stock.symbol,
        "name": Stock.name,
        "market": Stock.market,
        # 价格信息 (from StockQuote)
        "current_price": StockQuote.close,
        "change_percent": StockQuote.change_percent,
        "volume": StockQuote.volume,
        "market_cap": StockQuote.market_cap,
        # 财务指标 (from FinancialMetrics)
        "pe_ratio": FinancialMetrics.pe_ratio,
        "pb_ratio": FinancialMetrics.pb_ratio,
        "roe": FinancialMetrics.roe,
        "roa": FinancialMetrics.roa,
        "gross_margin": FinancialMetrics.gross_margin,
        "net_margin": FinancialMetrics.net_margin,
        "revenue_growth": FinancialMetrics.revenue_growth,
        "debt_to_equity": FinancialMetrics.debt_to_equity,
        "current_ratio": FinancialMetrics.current_ratio,
        "operating_margin": FinancialMetrics.operating_margin,
        "earnings_growth": FinancialMetrics.earnings_growth,
    }

    @staticmethod
    def _build_condition(condition: ScreenerCondition, field_obj):
        """构建单个筛选条件"""
        operator = condition.operator
        value = condition.value

        if operator == "gt":
            return field_obj > value
        elif operator == "gte":
            return field_obj >= value
        elif operator == "lt":
            return field_obj < value
        elif operator == "lte":
            return field_obj <= value
        elif operator == "eq":
            return field_obj == value
        elif operator == "ne":
            return field_obj != value
        elif operator == "between" and isinstance(value, list) and len(value) == 2:
            return and_(field_obj >= value[0], field_obj <= value[1])
        elif operator == "in" and isinstance(value, list):
            return field_obj.in_(value)
        else:
            return None

    @staticmethod
    async def screen_stocks(
        db: AsyncSession, request: ScreenerRequest
    ) -> tuple[list[dict[str, Any]], int]:
        """
        筛选股票

        Returns:
            (结果列表, 总数)
        """
        # 子查询：获取每只股票最新的报价
        latest_quote_subq = (
            select(
                StockQuote.stock_id,
                func.max(StockQuote.timestamp).label("max_timestamp"),
            )
            .group_by(StockQuote.stock_id)
            .subquery()
        )

        # 子查询：获取每只股票最新的财务指标
        latest_metrics_subq = (
            select(
                FinancialMetrics.symbol,
                FinancialMetrics.market,
                func.max(FinancialMetrics.report_date).label("max_date"),
            )
            .group_by(FinancialMetrics.symbol, FinancialMetrics.market)
            .subquery()
        )

        # 基础查询 - 联接 Stock, StockQuote, FinancialMetrics
        query = (
            select(Stock, StockQuote, FinancialMetrics)
            .outerjoin(
                latest_quote_subq,
                Stock.id == latest_quote_subq.c.stock_id,
            )
            .outerjoin(
                StockQuote,
                and_(
                    Stock.id == StockQuote.stock_id,
                    StockQuote.timestamp == latest_quote_subq.c.max_timestamp,
                ),
            )
            .outerjoin(
                latest_metrics_subq,
                and_(
                    Stock.symbol == latest_metrics_subq.c.symbol,
                    Stock.market == latest_metrics_subq.c.market,
                ),
            )
            .outerjoin(
                FinancialMetrics,
                and_(
                    Stock.symbol == FinancialMetrics.symbol,
                    Stock.market == FinancialMetrics.market,
                    FinancialMetrics.report_date == latest_metrics_subq.c.max_date,
                ),
            )
        )

        # 市场过滤
        if request.market != "ALL":
            query = query.where(Stock.market == request.market)

        # 应用筛选条件
        conditions = []
        for cond in request.conditions:
            field_obj = ScreenerService.FIELD_MAPPING.get(cond.field)
            if field_obj is not None:
                built_condition = ScreenerService._build_condition(cond, field_obj)
                if built_condition is not None:
                    conditions.append(built_condition)

        if conditions:
            query = query.where(and_(*conditions))

        # 计算总数
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar() or 0

        # 排序
        if request.order_by:
            order_field = ScreenerService.FIELD_MAPPING.get(request.order_by)
            if order_field is not None:
                if request.order_direction == "desc":
                    query = query.order_by(desc(order_field))
                else:
                    query = query.order_by(asc(order_field))

        # 分页
        query = query.offset(request.offset).limit(request.limit)

        # 执行查询
        result = await db.execute(query)
        rows = result.all()

        # 转换为结果列表
        results = []
        for stock, quote, metrics in rows:
            result_dict = {
                "symbol": stock.symbol,
                "name": stock.name,
                "market": stock.market,
            }

            # 添加报价数据
            if quote:
                result_dict.update(
                    {
                        "current_price": quote.close,
                        "change_percent": quote.change_percent,
                        "volume": quote.volume,
                        "market_cap": quote.market_cap,
                    }
                )

            # 添加财务指标
            if metrics:
                result_dict.update(
                    {
                        "pe_ratio": metrics.pe_ratio,
                        "pb_ratio": metrics.pb_ratio,
                        "roe": metrics.roe,
                        "roa": metrics.roa,
                        "gross_margin": metrics.gross_margin,
                        "net_margin": metrics.net_margin,
                        "revenue_growth": metrics.revenue_growth,
                        "debt_to_equity": metrics.debt_to_equity,
                    }
                )

            results.append(result_dict)

        return results, total

    @staticmethod
    async def get_available_fields() -> dict[str, Any]:
        """获取可用的筛选字段和运算符"""
        return {
            "fields": [
                {
                    "name": "current_price",
                    "label": "当前价格",
                    "category": "price",
                    "type": "number",
                },
                {
                    "name": "change_percent",
                    "label": "涨跌幅(%)",
                    "category": "price",
                    "type": "number",
                },
                {
                    "name": "volume",
                    "label": "成交量",
                    "category": "price",
                    "type": "number",
                },
                {
                    "name": "market_cap",
                    "label": "市值",
                    "category": "price",
                    "type": "number",
                },
                {
                    "name": "pe_ratio",
                    "label": "市盈率(PE)",
                    "category": "valuation",
                    "type": "number",
                },
                {
                    "name": "pb_ratio",
                    "label": "市净率(PB)",
                    "category": "valuation",
                    "type": "number",
                },
                {
                    "name": "roe",
                    "label": "净资产收益率(ROE)",
                    "category": "profitability",
                    "type": "number",
                },
                {
                    "name": "roa",
                    "label": "总资产收益率(ROA)",
                    "category": "profitability",
                    "type": "number",
                },
                {
                    "name": "gross_margin",
                    "label": "毛利率",
                    "category": "profitability",
                    "type": "number",
                },
                {
                    "name": "net_margin",
                    "label": "净利率",
                    "category": "profitability",
                    "type": "number",
                },
                {
                    "name": "revenue_growth",
                    "label": "营收增长率",
                    "category": "growth",
                    "type": "number",
                },
                {
                    "name": "debt_to_equity",
                    "label": "资产负债率",
                    "category": "solvency",
                    "type": "number",
                },
            ],
            "operators": [
                {"value": "gt", "label": "大于(>)"},
                {"value": "gte", "label": "大于等于(>=)"},
                {"value": "lt", "label": "小于(<)"},
                {"value": "lte", "label": "小于等于(<=)"},
                {"value": "eq", "label": "等于(=)"},
                {"value": "ne", "label": "不等于(!=)"},
                {"value": "between", "label": "区间"},
                {"value": "in", "label": "包含于"},
            ],
            "markets": [
                {"value": "ALL", "label": "全部市场"},
                {"value": "CN", "label": "A股"},
                {"value": "HK", "label": "港股"},
                {"value": "US", "label": "美股"},
            ],
        }
