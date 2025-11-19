"""API v1 路由"""

from fastapi import APIRouter
from app.api.v1 import auth, users, stocks, analysis

# 创建主路由
api_router = APIRouter()

# 注册子路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(stocks.router, prefix="/stocks", tags=["股票数据"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["分析任务"])

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
        ]
    }
