"""批量分析服务"""

import asyncio
from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import AnalysisTask
from app.models.batch_task import BatchAnalysisTask
from app.models.user_stock import UserStock
from app.models.stock import Stock
from app.schemas.batch_analysis import BatchAnalysisCreate
from app.services.analysis_service import AnalysisService
from app.core.websocket import websocket_manager


class BatchAnalysisService:
    """批量分析服务"""

    @staticmethod
    async def create_batch_task(
        db: AsyncSession, user_id: UUID, batch_create: BatchAnalysisCreate
    ) -> BatchAnalysisTask:
        """创建批量分析任务"""
        # 如果从自选股分组创建，获取该分组的股票列表
        symbols = batch_create.symbols
        markets = batch_create.markets

        if batch_create.from_watchlist_group:
            # 从自选股获取股票列表
            stmt = (
                select(UserStock, Stock)
                .join(Stock, UserStock.stock_id == Stock.id)
                .where(
                    and_(
                        UserStock.user_id == user_id,
                        UserStock.group_name == batch_create.from_watchlist_group,
                    )
                )
            )
            result = await db.execute(stmt)
            rows = result.all()

            symbols = [stock.symbol for _, stock in rows]
            markets = [stock.market for _, stock in rows]

        # 验证 symbols 和 markets 长度一致
        if len(symbols) != len(markets):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="symbols and markets must have the same length",
            )

        # 创建批量任务
        batch_task = BatchAnalysisTask(
            user_id=user_id,
            name=batch_create.name,
            parameters={
                "symbols": symbols,
                "markets": markets,
                "depth": batch_create.depth,
            },
            total_count=len(symbols),
            completed_count=0,
            failed_count=0,
            subtask_ids=[],
        )

        db.add(batch_task)
        await db.commit()
        await db.refresh(batch_task)

        return batch_task

    @staticmethod
    async def execute_batch_task(
        db: AsyncSession, batch_task_id: UUID, user_id: UUID
    ) -> None:
        """执行批量分析任务（异步后台运行）"""
        # 获取批量任务
        stmt = select(BatchAnalysisTask).where(BatchAnalysisTask.id == batch_task_id)
        result = await db.execute(stmt)
        batch_task = result.scalar_one_or_none()

        if not batch_task:
            return

        # 更新状态为运行中
        batch_task.status = "running"
        batch_task.started_at = datetime.now()
        await db.commit()

        # 获取参数
        symbols = batch_task.parameters["symbols"]
        markets = batch_task.parameters["markets"]
        depth = batch_task.parameters["depth"]

        subtask_ids = []

        # 逐个创建分析任务
        for i, (symbol, market) in enumerate(zip(symbols, markets)):
            try:
                # 广播进度
                await websocket_manager.broadcast_to_user(
                    user_id,
                    {
                        "type": "batch_analysis_progress",
                        "batch_task_id": str(batch_task_id),
                        "current_symbol": symbol,
                        "current_index": i + 1,
                        "total": len(symbols),
                        "completed": batch_task.completed_count,
                        "failed": batch_task.failed_count,
                    },
                )

                # 创建单个分析任务
                task = await AnalysisService.create_task(
                    db,
                    user_id,
                    {
                        "symbol": symbol,
                        "market": market,
                        "depth": depth,
                    },
                )
                subtask_ids.append(task.id)

                # 执行分析（在后台线程中）
                try:
                    await AnalysisService.run_analysis(db, task.id, user_id)
                    batch_task.completed_count += 1
                except Exception as e:
                    batch_task.failed_count += 1
                    # 继续执行其他任务，不中断

                await db.commit()

            except Exception as e:
                batch_task.failed_count += 1
                await db.commit()
                continue

        # 更新批量任务状态
        batch_task.subtask_ids = [str(sid) for sid in subtask_ids]
        batch_task.status = "completed" if batch_task.failed_count == 0 else "completed_with_errors"
        batch_task.completed_at = datetime.now()
        await db.commit()

        # 发送完成通知
        await websocket_manager.broadcast_to_user(
            user_id,
            {
                "type": "batch_analysis_completed",
                "batch_task_id": str(batch_task_id),
                "total": batch_task.total_count,
                "completed": batch_task.completed_count,
                "failed": batch_task.failed_count,
            },
        )

    @staticmethod
    async def get_batch_task(db: AsyncSession, batch_task_id: UUID) -> BatchAnalysisTask | None:
        """获取批量任务"""
        stmt = select(BatchAnalysisTask).where(BatchAnalysisTask.id == batch_task_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_batch_tasks(
        db: AsyncSession, user_id: UUID, limit: int = 20
    ) -> list[BatchAnalysisTask]:
        """获取用户的批量任务列表"""
        stmt = (
            select(BatchAnalysisTask)
            .where(BatchAnalysisTask.user_id == user_id)
            .order_by(BatchAnalysisTask.created_at.desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def cancel_batch_task(db: AsyncSession, batch_task_id: UUID, user_id: UUID) -> None:
        """取消批量任务"""
        stmt = select(BatchAnalysisTask).where(
            and_(
                BatchAnalysisTask.id == batch_task_id,
                BatchAnalysisTask.user_id == user_id,
            )
        )
        result = await db.execute(stmt)
        batch_task = result.scalar_one_or_none()

        if not batch_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Batch task not found",
            )

        if batch_task.status not in ["pending", "running"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending or running tasks can be cancelled",
            )

        batch_task.status = "cancelled"
        batch_task.completed_at = datetime.now()
        await db.commit()
