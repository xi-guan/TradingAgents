"""自选股服务"""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, and_, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stock import Stock
from app.models.user_stock import UserStock
from app.schemas.watchlist import WatchlistItemCreate, WatchlistItemUpdate
from app.services.stock_service import StockService


class WatchlistService:
    """自选股服务"""

    @staticmethod
    async def add_to_watchlist(
        db: AsyncSession, user_id: UUID, item_create: WatchlistItemCreate
    ) -> UserStock:
        """添加股票到自选股"""
        # 获取或创建股票
        stock = await StockService.get_or_create_stock(
            db, item_create.symbol, item_create.market
        )

        # 检查是否已经在自选股中
        stmt = select(UserStock).where(
            and_(
                UserStock.user_id == user_id,
                UserStock.stock_id == stock.id,
            )
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stock already in watchlist",
            )

        # 创建自选股记录
        user_stock = UserStock(
            user_id=user_id,
            stock_id=stock.id,
            group_name=item_create.group_name,
            notes=item_create.notes,
        )

        db.add(user_stock)
        await db.commit()
        await db.refresh(user_stock)

        return user_stock

    @staticmethod
    async def remove_from_watchlist(db: AsyncSession, user_id: UUID, item_id: UUID) -> None:
        """从自选股移除"""
        stmt = delete(UserStock).where(
            and_(
                UserStock.id == item_id,
                UserStock.user_id == user_id,
            )
        )
        result = await db.execute(stmt)

        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Watchlist item not found",
            )

        await db.commit()

    @staticmethod
    async def update_watchlist_item(
        db: AsyncSession, user_id: UUID, item_id: UUID, item_update: WatchlistItemUpdate
    ) -> UserStock:
        """更新自选股信息"""
        stmt = select(UserStock).where(
            and_(
                UserStock.id == item_id,
                UserStock.user_id == user_id,
            )
        )
        result = await db.execute(stmt)
        user_stock = result.scalar_one_or_none()

        if not user_stock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Watchlist item not found",
            )

        # 更新字段
        if item_update.group_name is not None:
            user_stock.group_name = item_update.group_name
        if item_update.notes is not None:
            user_stock.notes = item_update.notes

        await db.commit()
        await db.refresh(user_stock)

        return user_stock

    @staticmethod
    async def get_watchlist(
        db: AsyncSession, user_id: UUID, group_name: str | None = None
    ) -> list[dict]:
        """获取自选股列表（带实时行情）"""
        stmt = (
            select(UserStock, Stock)
            .join(Stock, UserStock.stock_id == Stock.id)
            .where(UserStock.user_id == user_id)
        )

        if group_name:
            stmt = stmt.where(UserStock.group_name == group_name)

        stmt = stmt.order_by(UserStock.created_at.desc())

        result = await db.execute(stmt)
        rows = result.all()

        # 构建响应数据
        watchlist_items = []
        for user_stock, stock in rows:
            # 获取实时行情
            quote = await StockService.fetch_and_save_quote(db, stock)

            item_data = {
                "id": user_stock.id,
                "user_id": user_stock.user_id,
                "stock_id": stock.id,
                "symbol": stock.symbol,
                "name": stock.name,
                "market": stock.market,
                "group_name": user_stock.group_name,
                "notes": user_stock.notes,
                "created_at": user_stock.created_at,
            }

            # 添加行情数据
            if quote:
                item_data["current_price"] = float(quote.close) if quote.close else None
                item_data["change"] = float(quote.change) if quote.change else None
                item_data["change_percent"] = float(quote.change_percent) if quote.change_percent else None

            watchlist_items.append(item_data)

        return watchlist_items

    @staticmethod
    async def get_groups(db: AsyncSession, user_id: UUID) -> list[dict]:
        """获取所有分组及其股票数量"""
        stmt = (
            select(UserStock.group_name, func.count(UserStock.id).label("count"))
            .where(UserStock.user_id == user_id)
            .group_by(UserStock.group_name)
            .order_by(UserStock.group_name)
        )

        result = await db.execute(stmt)
        groups = []

        for row in result:
            group_name = row.group_name or "默认分组"
            groups.append({
                "group_name": group_name,
                "count": row.count,
            })

        return groups

    @staticmethod
    async def check_in_watchlist(
        db: AsyncSession, user_id: UUID, symbol: str, market: str
    ) -> bool:
        """检查股票是否在自选股中"""
        # 先获取股票
        stmt = select(Stock).where(
            and_(
                Stock.symbol == symbol,
                Stock.market == market,
            )
        )
        result = await db.execute(stmt)
        stock = result.scalar_one_or_none()

        if not stock:
            return False

        # 检查是否在自选股中
        stmt = select(UserStock).where(
            and_(
                UserStock.user_id == user_id,
                UserStock.stock_id == stock.id,
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None
