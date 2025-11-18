"""API v1 路由"""

from fastapi import APIRouter

# 创建主路由
api_router = APIRouter()

# 导入子路由（稍后添加）
# from app.api.v1 import auth, stocks, analysis, trading, websocket

# 注册子路由
# api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
# api_router.include_router(stocks.router, prefix="/stocks", tags=["股票数据"])
# api_router.include_router(analysis.router, prefix="/analysis", tags=["分析任务"])
# api_router.include_router(trading.router, prefix="/trading", tags=["模拟交易"])
# api_router.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])

@api_router.get("/")
async def api_root():
    """API 根路径"""
    return {
        "version": "1.0",
        "endpoints": [
            "/auth",
            "/stocks",
            "/analysis",
            "/trading",
            "/ws"
        ]
    }
