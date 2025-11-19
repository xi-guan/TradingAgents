"""技术指标 API 路由"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.indicators_service import IndicatorsService

router = APIRouter()


@router.get("/{symbol}")
async def get_indicators(
    symbol: str,
    market: str = Query(..., pattern="^(CN|HK|US)$"),
    indicators: str = Query(
        default="sma,ema,rsi,macd,bbands",
        description="Comma-separated list of indicators: sma,ema,rsi,macd,bbands,kdj,obv",
    ),
    period: int = Query(default=14, ge=5, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    获取技术指标

    Parameters:
        - symbol: 股票代码
        - market: 市场 (CN, HK, US)
        - indicators: 指标列表，逗号分隔 (sma,ema,rsi,macd,bbands,kdj,obv)
        - period: 计算周期（天数），默认 14

    Returns:
        指标数据字典，包含各个指标的计算结果
    """
    # 解析指标列表
    indicator_list = [i.strip() for i in indicators.split(",")]

    # 计算指标
    results = await IndicatorsService.calculate_indicators(
        db, symbol, market, indicator_list, period
    )

    return {
        "symbol": symbol,
        "market": market,
        "period": period,
        "indicators": results,
    }


@router.get("/{symbol}/all")
async def get_all_indicators(
    symbol: str,
    market: str = Query(..., pattern="^(CN|HK|US)$"),
    period: int = Query(default=14, ge=5, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    获取所有技术指标

    Parameters:
        - symbol: 股票代码
        - market: 市场 (CN, HK, US)
        - period: 计算周期（天数），默认 14

    Returns:
        所有技术指标数据
    """
    results = await IndicatorsService.get_all_indicators(db, symbol, market, period)

    return {
        "symbol": symbol,
        "market": market,
        "period": period,
        "indicators": results,
    }
