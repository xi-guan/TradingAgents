"""交易账户服务"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trading import TradingAccount, Position, Order
from app.schemas.trading import TradingAccountCreate, OrderCreate
from app.services.stock_service import StockService


class TradingAccountService:
    """交易账户服务"""

    @staticmethod
    async def create_account(
        db: AsyncSession, user_id: UUID, account_create: TradingAccountCreate
    ) -> TradingAccount:
        """创建交易账户"""
        # 检查用户是否已有账户
        stmt = select(TradingAccount).where(TradingAccount.user_id == user_id)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has a trading account",
            )

        # 创建账户
        account = TradingAccount(
            user_id=user_id,
            account_type=account_create.account_type,
        )

        # 根据市场设置初始资金
        if account_create.market == "CN":
            account.cash_cny = account_create.initial_cash
        elif account_create.market == "HK":
            account.cash_hkd = account_create.initial_cash
        else:  # US
            account.cash_usd = account_create.initial_cash

        db.add(account)
        await db.commit()
        await db.refresh(account)

        return account

    @staticmethod
    async def get_or_create_default_account(
        db: AsyncSession, user_id: UUID, market: str = "CN"
    ) -> TradingAccount:
        """获取或创建默认账户"""
        # 尝试获取现有账户
        stmt = select(TradingAccount).where(TradingAccount.user_id == user_id)
        result = await db.execute(stmt)
        account = result.scalar_one_or_none()

        if account:
            return account

        # 创建默认账户
        default_create = TradingAccountCreate(
            account_type="paper",
            market=market,
            initial_cash=Decimal("1000000") if market == "CN" else Decimal("100000"),
        )
        return await TradingAccountService.create_account(db, user_id, default_create)

    @staticmethod
    async def get_account_by_id(db: AsyncSession, account_id: UUID) -> TradingAccount | None:
        """根据 ID 获取账户"""
        stmt = select(TradingAccount).where(TradingAccount.id == account_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_accounts(db: AsyncSession, user_id: UUID) -> list[TradingAccount]:
        """获取用户所有账户"""
        stmt = select(TradingAccount).where(TradingAccount.user_id == user_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def create_order(
        db: AsyncSession, account_id: UUID, order_create: OrderCreate
    ) -> Order:
        """创建订单"""
        # 获取账户
        account = await TradingAccountService.get_account_by_id(db, account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found",
            )

        # 获取当前价格（如果是市价单）
        price = order_create.price
        if order_create.order_type == "market":
            # 获取实时价格
            try:
                stock = await StockService.get_or_create_stock(
                    db, order_create.symbol, order_create.market
                )
                quote = await StockService.fetch_and_save_quote(db, stock)
                if quote and quote.close:
                    price = quote.close
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Unable to fetch current price for market order",
                    )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to fetch price: {str(e)}",
                )
        else:
            # 限价单必须提供价格
            if not price:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Price is required for limit orders",
                )

        # 计算订单金额
        total_cost = price * Decimal(order_create.quantity)

        # 获取对应市场的现金余额
        if order_create.market == "CN":
            cash_balance = account.cash_cny
        elif order_create.market == "HK":
            cash_balance = account.cash_hkd
        else:  # US
            cash_balance = account.cash_usd

        # 买入订单：检查资金是否足够
        if order_create.side == "buy":
            if cash_balance < total_cost:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Insufficient funds",
                )

            # 扣除资金
            if order_create.market == "CN":
                account.cash_cny -= total_cost
            elif order_create.market == "HK":
                account.cash_hkd -= total_cost
            else:
                account.cash_usd -= total_cost

        # 卖出订单：检查持仓是否足够
        elif order_create.side == "sell":
            stmt = select(Position).where(
                and_(
                    Position.account_id == account_id,
                    Position.symbol == order_create.symbol,
                    Position.market == order_create.market,
                )
            )
            result = await db.execute(stmt)
            position = result.scalar_one_or_none()

            if not position or position.quantity < order_create.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Insufficient position",
                )

        # 创建订单（模拟交易，立即成交）
        order = Order(
            account_id=account_id,
            symbol=order_create.symbol,
            market=order_create.market,
            side=order_create.side,
            order_type=order_create.order_type,
            quantity=order_create.quantity,
            price=order_create.price,
            filled_quantity=order_create.quantity,
            filled_price=price,
            status="filled",
            filled_at=datetime.now(),
        )

        db.add(order)

        # 更新持仓
        if order_create.side == "buy":
            await TradingAccountService._update_position_buy(
                db, account_id, order_create.symbol, order_create.market, order_create.quantity, price
            )
        else:  # sell
            await TradingAccountService._update_position_sell(
                db, account_id, order_create.symbol, order_create.market, order_create.quantity, price
            )

        await db.commit()
        await db.refresh(order)

        return order

    @staticmethod
    async def _update_position_buy(
        db: AsyncSession, account_id: UUID, symbol: str, market: str, quantity: int, price: Decimal
    ):
        """更新持仓（买入）"""
        # 查找现有持仓
        stmt = select(Position).where(
            and_(
                Position.account_id == account_id,
                Position.symbol == symbol,
                Position.market == market,
            )
        )
        result = await db.execute(stmt)
        position = result.scalar_one_or_none()

        if position:
            # 更新现有持仓
            total_quantity = position.quantity + quantity
            total_cost = (position.avg_cost * position.quantity) + (price * quantity)
            position.avg_cost = total_cost / total_quantity
            position.quantity = total_quantity
            position.current_price = price
        else:
            # 创建新持仓
            position = Position(
                account_id=account_id,
                symbol=symbol,
                market=market,
                quantity=quantity,
                avg_cost=price,
                current_price=price,
            )
            db.add(position)

    @staticmethod
    async def _update_position_sell(
        db: AsyncSession, account_id: UUID, symbol: str, market: str, quantity: int, price: Decimal
    ):
        """更新持仓（卖出）"""
        # 查找现有持仓
        stmt = select(Position).where(
            and_(
                Position.account_id == account_id,
                Position.symbol == symbol,
                Position.market == market,
            )
        )
        result = await db.execute(stmt)
        position = result.scalar_one_or_none()

        if not position:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Position not found",
            )

        # 更新持仓数量
        position.quantity -= quantity
        position.current_price = price

        # 如果持仓清空，删除记录
        if position.quantity <= 0:
            await db.delete(position)

        # 返还资金到账户
        account = await TradingAccountService.get_account_by_id(db, account_id)
        total_proceeds = price * quantity

        if market == "CN":
            account.cash_cny += total_proceeds
        elif market == "HK":
            account.cash_hkd += total_proceeds
        else:
            account.cash_usd += total_proceeds

    @staticmethod
    async def get_orders(
        db: AsyncSession, account_id: UUID, status_filter: str | None = None
    ) -> list[Order]:
        """获取订单列表"""
        stmt = select(Order).where(Order.account_id == account_id)

        if status_filter:
            stmt = stmt.where(Order.status == status_filter)

        stmt = stmt.order_by(Order.created_at.desc())

        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_order(db: AsyncSession, order_id: UUID) -> Order | None:
        """获取订单详情"""
        stmt = select(Order).where(Order.id == order_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def cancel_order(db: AsyncSession, order_id: UUID) -> Order:
        """取消订单"""
        order = await TradingAccountService.get_order(db, order_id)

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )

        # 只有待成交的订单可以取消
        if order.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending orders can be cancelled",
            )

        # 更新订单状态
        order.status = "cancelled"

        # 如果是买入订单，退还资金
        if order.side == "buy" and order.price:
            account = await TradingAccountService.get_account_by_id(db, order.account_id)
            refund = order.price * (order.quantity - order.filled_quantity)

            if order.market == "CN":
                account.cash_cny += refund
            elif order.market == "HK":
                account.cash_hkd += refund
            else:
                account.cash_usd += refund

        await db.commit()
        await db.refresh(order)

        return order

    @staticmethod
    async def get_positions(db: AsyncSession, account_id: UUID) -> list[Position]:
        """获取持仓列表"""
        stmt = (
            select(Position)
            .where(Position.account_id == account_id)
            .where(Position.quantity > 0)
            .order_by(Position.created_at.desc())
        )

        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def update_position_price(db: AsyncSession, position: Position) -> Position:
        """更新持仓价格"""
        try:
            # 获取最新价格
            stock = await StockService.get_or_create_stock(db, position.symbol, position.market)
            quote = await StockService.fetch_and_save_quote(db, stock)

            if quote and quote.close:
                position.current_price = quote.close
                position.unrealized_pnl = (quote.close - position.avg_cost) * position.quantity
                await db.commit()
                await db.refresh(position)
        except Exception:
            # 如果无法获取价格，保持原有价格
            pass

        return position
