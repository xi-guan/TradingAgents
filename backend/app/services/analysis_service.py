"""分析任务服务"""

from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.analysis import AnalysisTask
from app.schemas.analysis import AnalysisTaskCreate


class AnalysisService:
    """分析任务服务"""

    @staticmethod
    async def create_task(
        db: AsyncSession,
        user_id: str,
        task_create: AnalysisTaskCreate,
    ) -> AnalysisTask:
        """创建分析任务"""
        # 默认使用今天的日期
        analysis_date = task_create.analysis_date or datetime.now().strftime("%Y-%m-%d")

        task = AnalysisTask(
            user_id=user_id,
            symbol=task_create.symbol,
            market=task_create.market,
            analysis_date=analysis_date,
            depth=task_create.depth,
            status="pending",
            progress=0,
        )

        db.add(task)
        await db.commit()
        await db.refresh(task)

        return task

    @staticmethod
    async def get_task(db: AsyncSession, task_id: str, user_id: str) -> AnalysisTask | None:
        """获取任务"""
        result = await db.execute(
            select(AnalysisTask).where(
                and_(
                    AnalysisTask.id == task_id,
                    AnalysisTask.user_id == user_id,
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_tasks(
        db: AsyncSession,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[AnalysisTask]:
        """获取用户的分析任务"""
        result = await db.execute(
            select(AnalysisTask)
            .where(AnalysisTask.user_id == user_id)
            .order_by(AnalysisTask.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def update_task_progress(
        db: AsyncSession,
        task_id: str,
        progress: int,
        status: str | None = None,
    ) -> AnalysisTask | None:
        """更新任务进度"""
        result = await db.execute(
            select(AnalysisTask).where(AnalysisTask.id == task_id)
        )
        task = result.scalar_one_or_none()

        if not task:
            return None

        task.progress = progress
        if status:
            task.status = status

        await db.commit()
        await db.refresh(task)

        return task

    @staticmethod
    async def update_task_result(
        db: AsyncSession,
        task_id: str,
        result: dict,
    ) -> AnalysisTask | None:
        """更新任务结果"""
        task_result = await db.execute(
            select(AnalysisTask).where(AnalysisTask.id == task_id)
        )
        task = task_result.scalar_one_or_none()

        if not task:
            return None

        task.result = result
        task.status = "completed"
        task.progress = 100

        await db.commit()
        await db.refresh(task)

        return task

    @staticmethod
    async def delete_task(db: AsyncSession, task_id: str, user_id: str) -> bool:
        """删除任务"""
        result = await db.execute(
            select(AnalysisTask).where(
                and_(
                    AnalysisTask.id == task_id,
                    AnalysisTask.user_id == user_id,
                )
            )
        )
        task = result.scalar_one_or_none()

        if not task:
            return False

        await db.delete(task)
        await db.commit()

        return True
