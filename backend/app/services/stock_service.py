"""股票数据服务"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data_providers.factory import DataProviderFactory
from app.models.stock import Stock, StockHistory, StockQuote
from app.utils.market_utils import normalize_symbol


class StockService:
    """股票数据服务"""

    @staticmethod
    async def search_stocks(
        db: AsyncSession, query: str, market: str | None = None, limit: int = 10
    ) -> list[Stock]:
        """
        搜索股票

        Args:
            db: 数据库会话
            query: 搜索关键词
            market: 市场类型（可选，用于过滤）
            limit: 返回数量限制

        Returns:
            股票列表
        """
        # 首先尝试从数据库搜索
        stmt = select(Stock).where(
            (Stock.symbol.ilike(f"%{query}%")) | (Stock.name.ilike(f"%{query}%"))
        )

        if market:
            stmt = stmt.where(Stock.market == market)

        stmt = stmt.limit(limit)

        result = await db.execute(stmt)
        stocks = list(result.scalars().all())

        # 如果数据库中没有，尝试从数据源搜索
        if not stocks:
            # 如果提供了市场类型，使用对应的数据提供者
            if market:
                provider = DataProviderFactory.get_provider(market)
                search_results = await provider.search_stocks(query, limit)

                # 将搜索结果转换为 Stock 对象（但不保存）
                stocks = [
                    Stock(
                        symbol=item["symbol"],
                        name=item["name"],
                        market=item["market"],
                        sector=item.get("sector"),
                        industry=item.get("industry"),
                    )
                    for item in search_results
                ]
            else:
                # 如果没有指定市场，尝试所有数据提供者
                all_results = []

                # A 股
                for provider in DataProviderFactory.get_all_cn_providers():
                    results = await provider.search_stocks(query, limit)
                    all_results.extend(results)
                    if len(all_results) >= limit:
                        break

                # 美股
                if len(all_results) < limit:
                    yf_provider = DataProviderFactory.get_yfinance()
                    yf_results = await yf_provider.search_stocks(query, limit - len(all_results))
                    all_results.extend(yf_results)

                stocks = [
                    Stock(
                        symbol=item["symbol"],
                        name=item["name"],
                        market=item["market"],
                        sector=item.get("sector"),
                        industry=item.get("industry"),
                    )
                    for item in all_results[:limit]
                ]

        return stocks

    @staticmethod
    async def get_stock_by_id(db: AsyncSession, stock_id: UUID) -> Stock | None:
        """根据 ID 获取股票"""
        result = await db.execute(select(Stock).where(Stock.id == stock_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_stock_info(
        db: AsyncSession, symbol: str, market: str
    ) -> Stock | None:
        """获取股票信息"""
        result = await db.execute(
            select(Stock).where(and_(Stock.symbol == symbol, Stock.market == market))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_or_create_stock(
        db: AsyncSession, symbol: str, market: str | None = None
    ) -> Stock:
        """
        获取或创建股票

        Args:
            db: 数据库会话
            symbol: 股票代码
            market: 市场类型（可选，如果不提供则自动检测）

        Returns:
            股票对象
        """
        # 标准化股票代码
        normalized_symbol, detected_market = normalize_symbol(symbol)

        # 使用提供的市场或检测到的市场
        final_market = market or detected_market

        # 检查是否已存在
        stock = await StockService.get_stock_info(db, symbol, final_market)
        if stock:
            return stock

        # 从数据提供者获取股票信息
        provider = DataProviderFactory.get_provider(final_market)
        stock_info = await provider.get_stock_info(symbol)

        if stock_info:
            stock = Stock(
                symbol=symbol,
                name=stock_info["name"],
                market=final_market,
                sector=stock_info.get("sector"),
                industry=stock_info.get("industry"),
                description=stock_info.get("description"),
            )
        else:
            # 如果无法获取信息，创建基本记录
            stock = Stock(
                symbol=symbol,
                name=symbol,
                market=final_market,
            )

        db.add(stock)
        await db.commit()
        await db.refresh(stock)

        return stock

    @staticmethod
    async def get_latest_quote(
        db: AsyncSession, stock_id: UUID
    ) -> StockQuote | None:
        """获取最新行情"""
        result = await db.execute(
            select(StockQuote)
            .where(StockQuote.stock_id == stock_id)
            .order_by(StockQuote.timestamp.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def fetch_and_save_quote(
        db: AsyncSession, stock: Stock
    ) -> StockQuote | None:
        """
        从数据源获取并保存最新行情

        Args:
            db: 数据库会话
            stock: 股票对象

        Returns:
            行情对象
        """
        provider = DataProviderFactory.get_provider(stock.market)
        quote_data = await provider.get_realtime_quote(stock.symbol)

        if not quote_data:
            return None

        # 创建或更新行情记录
        quote = StockQuote(
            stock_id=stock.id,
            timestamp=quote_data["timestamp"],
            open=quote_data.get("open"),
            high=quote_data.get("high"),
            low=quote_data.get("low"),
            close=quote_data["close"],
            volume=quote_data.get("volume"),
            prev_close=quote_data.get("prev_close"),
            change=quote_data.get("change"),
            change_percent=quote_data.get("change_percent"),
        )

        db.add(quote)
        await db.commit()
        await db.refresh(quote)

        return quote

    @staticmethod
    async def get_historical_data(
        db: AsyncSession,
        stock_id: UUID,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d",
    ) -> list[StockHistory]:
        """获取历史数据"""
        result = await db.execute(
            select(StockHistory)
            .where(
                and_(
                    StockHistory.stock_id == stock_id,
                    StockHistory.timestamp >= start_date,
                    StockHistory.timestamp <= end_date,
                    StockHistory.interval == interval,
                )
            )
            .order_by(StockHistory.timestamp.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def fetch_and_save_history(
        db: AsyncSession,
        stock: Stock,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d",
    ) -> list[StockHistory]:
        """
        从数据源获取并保存历史数据

        Args:
            db: 数据库会话
            stock: 股票对象
            start_date: 开始日期
            end_date: 结束日期
            interval: 时间间隔

        Returns:
            历史数据列表
        """
        provider = DataProviderFactory.get_provider(stock.market)
        history_data = await provider.get_historical_data(
            stock.symbol, start_date, end_date, interval
        )

        if not history_data:
            return []

        # 批量保存历史数据
        history_records = []
        for data in history_data:
            # 检查是否已存在
            existing = await db.execute(
                select(StockHistory).where(
                    and_(
                        StockHistory.stock_id == stock.id,
                        StockHistory.timestamp == data["timestamp"],
                        StockHistory.interval == interval,
                    )
                )
            )

            if existing.scalar_one_or_none():
                continue

            history = StockHistory(
                stock_id=stock.id,
                timestamp=data["timestamp"],
                open=data.get("open"),
                high=data.get("high"),
                low=data.get("low"),
                close=data["close"],
                volume=data.get("volume"),
                adj_close=data.get("adj_close"),
                interval=interval,
            )

            db.add(history)
            history_records.append(history)

        if history_records:
            await db.commit()
            for record in history_records:
                await db.refresh(record)

        return history_records
