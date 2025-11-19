"""股票数据 API"""

from typing import Annotated
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies import CurrentUser
from app.schemas.stock import StockInfo, StockQuote, StockHistory, StockSearch
from app.services.stock_service import StockService

router = APIRouter()


@router.get("/search", response_model=list[StockSearch])
async def search_stocks(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(10, ge=1, le=50),
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser = None,  # 可选认证
):
    """搜索股票"""
    stocks = await StockService.search_stocks(db, q, limit)

    return [
        StockSearch(
            symbol=stock.symbol,
            name=stock.name,
            market=stock.market,
            full_symbol=stock.full_symbol,
        )
        for stock in stocks
    ]


@router.get("/{symbol}", response_model=StockInfo)
async def get_stock_info(
    symbol: str,
    market: str = Query(..., pattern="^(CN|HK|US)$"),
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser = None,
):
    """获取股票详情"""
    stock = await StockService.get_or_create_stock(db, symbol, market)

    if not stock:
        raise HTTPException(status_code=404, detail="股票不存在")

    return StockInfo.model_validate(stock)


@router.get("/{symbol}/quote", response_model=StockQuote)
async def get_stock_quote(
    symbol: str,
    market: str = Query(..., pattern="^(CN|HK|US)$"),
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser = None,
):
    """获取实时行情"""
    quote = await StockService.get_realtime_quote(db, symbol, market)

    if not quote:
        raise HTTPException(status_code=404, detail="行情数据不存在")

    return StockQuote.model_validate(quote)


@router.get("/{symbol}/history", response_model=list[StockHistory])
async def get_stock_history(
    symbol: str,
    market: str = Query(..., pattern="^(CN|HK|US)$"),
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser = None,
):
    """获取历史数据"""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误")

    history = await StockService.get_historical_data(db, symbol, market, start, end)

    return [StockHistory.model_validate(h) for h in history]
