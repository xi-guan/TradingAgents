"""交易 API 路由"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import CurrentUser
from app.schemas.trading import (
    OrderCreate,
    OrderResponse,
    PositionResponse,
    TradingAccountCreate,
    TradingAccountResponse,
)
from app.services.trading_account_service import TradingAccountService

router = APIRouter()


@router.post("/account", response_model=TradingAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    account_create: TradingAccountCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """创建交易账户"""
    account = await TradingAccountService.create_account(
        db, current_user.id, account_create
    )
    return account


@router.get("/account", response_model=TradingAccountResponse)
async def get_account(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    market: str = "CN",
):
    """获取交易账户信息"""
    account = await TradingAccountService.get_or_create_default_account(
        db, current_user.id, market
    )
    return account


@router.get("/accounts", response_model=list[TradingAccountResponse])
async def list_accounts(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """获取所有交易账户"""
    accounts = await TradingAccountService.get_user_accounts(db, current_user.id)
    return accounts


@router.get("/positions", response_model=list[PositionResponse])
async def list_positions(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    market: str = "CN",
):
    """获取持仓列表"""
    account = await TradingAccountService.get_or_create_default_account(
        db, current_user.id, market
    )
    positions = await TradingAccountService.get_positions(db, account.id)

    # 更新持仓的当前价格和盈亏
    for position in positions:
        await TradingAccountService.update_position_price(db, position)

    return positions


@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_create: OrderCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """创建订单"""
    # 获取或创建账户
    account = await TradingAccountService.get_or_create_default_account(
        db, current_user.id, order_create.market
    )

    # 创建订单
    order = await TradingAccountService.create_order(
        db, account.id, order_create
    )

    return order


@router.get("/orders", response_model=list[OrderResponse])
async def list_orders(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    market: str = "CN",
    status_filter: str | None = None,
):
    """获取订单列表"""
    account = await TradingAccountService.get_or_create_default_account(
        db, current_user.id, market
    )
    orders = await TradingAccountService.get_orders(
        db, account.id, status_filter
    )
    return orders


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """获取订单详情"""
    order = await TradingAccountService.get_order(db, order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # 验证订单所属账户是否属于当前用户
    account = await TradingAccountService.get_account_by_id(db, order.account_id)
    if account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this order"
        )

    return order


@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_order(
    order_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """取消订单"""
    order = await TradingAccountService.get_order(db, order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # 验证订单所属账户是否属于当前用户
    account = await TradingAccountService.get_account_by_id(db, order.account_id)
    if account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this order"
        )

    # 取消订单
    await TradingAccountService.cancel_order(db, order_id)
