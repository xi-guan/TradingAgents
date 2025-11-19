"""新闻数据服务"""

import asyncio
from datetime import datetime, timedelta
from typing import Any

import httpx
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.news import NewsArticle


class NewsService:
    """新闻数据服务"""

    @staticmethod
    async def fetch_news_from_alpha_vantage(
        symbol: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        """从 Alpha Vantage 获取新闻（需要 API key）"""
        if not settings.alpha_vantage_api_key:
            return []

        url = "https://www.alphavantage.co/query"
        params = {
            "function": "NEWS_SENTIMENT",
            "tickers": symbol,
            "apikey": settings.alpha_vantage_api_key,
            "limit": limit,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                data = response.json()

                if "feed" not in data:
                    return []

                articles = []
                for item in data["feed"][:limit]:
                    # 解析 Alpha Vantage 新闻格式
                    article = {
                        "title": item.get("title", ""),
                        "summary": item.get("summary", ""),
                        "url": item.get("url", ""),
                        "source": item.get("source", "Alpha Vantage"),
                        "author": item.get("authors", [None])[0] if item.get("authors") else None,
                        "published_at": datetime.fromisoformat(
                            item.get("time_published", "").replace("Z", "+00:00")
                        )
                        if item.get("time_published")
                        else datetime.now(),
                        "sentiment": None,
                        "sentiment_score": None,
                    }

                    # 提取情感分析（如果有）
                    if "overall_sentiment_score" in item:
                        score = float(item["overall_sentiment_score"])
                        article["sentiment_score"] = score
                        if score > 0.15:
                            article["sentiment"] = "positive"
                        elif score < -0.15:
                            article["sentiment"] = "negative"
                        else:
                            article["sentiment"] = "neutral"

                    articles.append(article)

                return articles

        except Exception as e:
            print(f"Error fetching news from Alpha Vantage: {e}")
            return []

    @staticmethod
    async def save_news(
        db: AsyncSession, symbol: str, market: str, articles: list[dict[str, Any]]
    ) -> list[NewsArticle]:
        """保存新闻到数据库（去重）"""
        saved_articles = []

        for article_data in articles:
            # 检查是否已存在（通过 URL）
            stmt = select(NewsArticle).where(NewsArticle.url == article_data["url"])
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                continue

            # 创建新记录
            article = NewsArticle(
                symbol=symbol,
                market=market,
                title=article_data["title"],
                summary=article_data.get("summary"),
                content=article_data.get("content"),
                url=article_data["url"],
                source=article_data["source"],
                author=article_data.get("author"),
                sentiment=article_data.get("sentiment"),
                sentiment_score=article_data.get("sentiment_score"),
                published_at=article_data["published_at"],
            )

            db.add(article)
            saved_articles.append(article)

        if saved_articles:
            await db.commit()
            for article in saved_articles:
                await db.refresh(article)

        return saved_articles

    @staticmethod
    async def get_news(
        db: AsyncSession,
        symbol: str,
        market: str,
        limit: int = 10,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        fetch_if_empty: bool = True,
    ) -> list[NewsArticle]:
        """获取新闻（优先从数据库，如果为空则从 API 获取）"""
        # 构建查询
        stmt = (
            select(NewsArticle)
            .where(
                and_(
                    NewsArticle.symbol == symbol,
                    NewsArticle.market == market,
                )
            )
            .order_by(desc(NewsArticle.published_at))
            .limit(limit)
        )

        # 添加日期过滤
        if from_date:
            stmt = stmt.where(NewsArticle.published_at >= from_date)
        if to_date:
            stmt = stmt.where(NewsArticle.published_at <= to_date)

        result = await db.execute(stmt)
        articles = list(result.scalars().all())

        # 如果数据库为空且允许获取，则从 API 获取
        if not articles and fetch_if_empty:
            # 从 Alpha Vantage 获取
            fetched_articles = await NewsService.fetch_news_from_alpha_vantage(
                symbol, limit
            )
            if fetched_articles:
                articles = await NewsService.save_news(
                    db, symbol, market, fetched_articles
                )

        return articles

    @staticmethod
    async def get_latest_news(
        db: AsyncSession, symbol: str, market: str, hours: int = 24, limit: int = 10
    ) -> list[NewsArticle]:
        """获取最近 N 小时的新闻"""
        from_date = datetime.now() - timedelta(hours=hours)
        return await NewsService.get_news(
            db, symbol, market, limit=limit, from_date=from_date
        )
