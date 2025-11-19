"""新闻数据 API 路由"""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.news import NewsArticleResponse
from app.services.news_service import NewsService

router = APIRouter()


@router.get("/{symbol}", response_model=list[NewsArticleResponse])
async def get_stock_news(
    symbol: str,
    market: str = Query(..., pattern="^(CN|HK|US)$"),
    limit: int = Query(default=10, ge=1, le=100),
    hours: int = Query(default=None, ge=1, le=720),  # 最近 N 小时
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    db: AsyncSession = Depends(get_db),
):
    """
    获取股票新闻

    Parameters:
        - symbol: 股票代码
        - market: 市场 (CN, HK, US)
        - limit: 返回数量（最多 100）
        - hours: 获取最近 N 小时的新闻（可选）
        - from_date: 开始日期（可选）
        - to_date: 结束日期（可选）

    Returns:
        新闻列表，按发布时间倒序
    """
    if hours:
        return await NewsService.get_latest_news(db, symbol, market, hours, limit)
    else:
        return await NewsService.get_news(
            db, symbol, market, limit, from_date, to_date
        )


@router.post("/{symbol}/refresh", response_model=list[NewsArticleResponse])
async def refresh_stock_news(
    symbol: str,
    market: str = Query(..., pattern="^(CN|HK|US)$"),
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    强制刷新股票新闻（从 API 获取最新数据）

    Parameters:
        - symbol: 股票代码
        - market: 市场 (CN, HK, US)
        - limit: 返回数量（最多 100）

    Returns:
        新闻列表
    """
    # 从 API 获取
    articles_data = await NewsService.fetch_news_from_alpha_vantage(symbol, limit)

    # 保存到数据库
    articles = await NewsService.save_news(db, symbol, market, articles_data)

    # 返回最新数据
    return await NewsService.get_news(db, symbol, market, limit, fetch_if_empty=False)
