"""自选股 API 路由"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import CurrentUser
from app.schemas.watchlist import (
    WatchlistItemCreate,
    WatchlistItemUpdate,
    WatchlistItemResponse,
    WatchlistGroupResponse,
)
from app.services.watchlist_service import WatchlistService

router = APIRouter()


@router.post("", response_model=WatchlistItemResponse, status_code=status.HTTP_201_CREATED)
async def add_to_watchlist(
    item_create: WatchlistItemCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """添加股票到自选股"""
    user_stock = await WatchlistService.add_to_watchlist(db, current_user.id, item_create)

    # 获取完整数据以返回
    watchlist = await WatchlistService.get_watchlist(db, current_user.id)

    # 找到刚添加的项
    for item in watchlist:
        if item["id"] == user_stock.id:
            return item

    # 如果没找到，返回基本信息
    return {
        "id": user_stock.id,
        "user_id": user_stock.user_id,
        "stock_id": user_stock.stock_id,
        "group_name": user_stock.group_name,
        "notes": user_stock.notes,
        "created_at": user_stock.created_at,
    }


@router.get("", response_model=list[WatchlistItemResponse])
async def get_watchlist(
    current_user: CurrentUser,
    group_name: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """获取自选股列表"""
    return await WatchlistService.get_watchlist(db, current_user.id, group_name)


@router.get("/groups", response_model=list[WatchlistGroupResponse])
async def get_groups(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """获取所有分组"""
    groups_data = await WatchlistService.get_groups(db, current_user.id)

    # 为每个分组获取股票列表
    result = []
    for group_data in groups_data:
        group_name = group_data["group_name"]
        actual_group_name = None if group_name == "默认分组" else group_name

        stocks = await WatchlistService.get_watchlist(db, current_user.id, actual_group_name)

        result.append({
            "group_name": group_name,
            "count": group_data["count"],
            "stocks": stocks,
        })

    return result


@router.get("/check/{symbol}")
async def check_in_watchlist(
    symbol: str,
    market: str = Query(..., pattern="^(CN|HK|US)$"),
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """检查股票是否在自选股中"""
    in_watchlist = await WatchlistService.check_in_watchlist(
        db, current_user.id, symbol, market
    )
    return {"in_watchlist": in_watchlist}


@router.put("/{item_id}", response_model=WatchlistItemResponse)
async def update_watchlist_item(
    item_id: UUID,
    item_update: WatchlistItemUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """更新自选股信息"""
    user_stock = await WatchlistService.update_watchlist_item(
        db, current_user.id, item_id, item_update
    )

    # 获取完整数据以返回
    watchlist = await WatchlistService.get_watchlist(db, current_user.id)

    # 找到更新的项
    for item in watchlist:
        if item["id"] == user_stock.id:
            return item

    # 如果没找到，返回基本信息
    return {
        "id": user_stock.id,
        "user_id": user_stock.user_id,
        "stock_id": user_stock.stock_id,
        "group_name": user_stock.group_name,
        "notes": user_stock.notes,
        "created_at": user_stock.created_at,
    }


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_watchlist(
    item_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """从自选股移除"""
    await WatchlistService.remove_from_watchlist(db, current_user.id, item_id)
