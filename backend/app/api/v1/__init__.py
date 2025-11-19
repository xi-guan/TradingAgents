"""API v1 路由"""

from fastapi import APIRouter
from app.api.v1 import auth, users, stocks, analysis, trading, indicators, watchlist, batch_analysis, news, financials

# 创建主路由
api_router = APIRouter()

# 注册子路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(stocks.router, prefix="/stocks", tags=["股票数据"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["分析任务"])
api_router.include_router(trading.router, prefix="/trading", tags=["模拟交易"])
api_router.include_router(indicators.router, prefix="/indicators", tags=["技术指标"])
api_router.include_router(watchlist.router, prefix="/watchlist", tags=["自选股"])
api_router.include_router(batch_analysis.router, prefix="/batch-analysis", tags=["批量分析"])
api_router.include_router(news.router, prefix="/news", tags=["新闻数据"])
api_router.include_router(financials.router, prefix="/financials", tags=["财务数据"])

@api_router.get("/")
async def api_root():
    """API 根路径"""
    return {
        "version": "1.0",
        "endpoints": [
            "/auth",
            "/users",
            "/stocks",
            "/analysis",
            "/trading",
            "/indicators",
            "/watchlist",
            "/batch-analysis",
            "/news",
            "/financials",
        ]
    }
