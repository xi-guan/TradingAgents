"""分析任务（后台任务）"""

from datetime import datetime
from uuid import UUID

from app.core.database import async_session_maker
from app.core.websocket_manager import websocket_manager
from app.services.analysis_service import AnalysisService
from app.services.trading_service import TradingService


async def run_analysis_task(task_id: str | UUID):
    """运行分析任务"""
    async with async_session_maker() as db:
        # 获取任务
        task = await AnalysisService.get_task(db, UUID(task_id) if isinstance(task_id, str) else task_id)

        if not task:
            return

        try:
            # 更新任务状态为运行中
            await AnalysisService.update_task_progress(db, task.id, 5, "running")

            # 推送初始进度
            await websocket_manager.broadcast_to_user(
                str(task.user_id),
                {
                    "type": "analysis_progress",
                    "task_id": str(task.id),
                    "progress": 5,
                    "stage": "initializing",
                    "message": "初始化分析任务...",
                    "timestamp": datetime.now().isoformat(),
                },
            )

            # 构造分析参数
            parameters = {
                "company_name": task.symbol,
                "trade_date": task.analysis_date,
                "selected_analysts": ["market", "social", "news", "fundamentals"],
            }

            # 根据 depth 参数调整分析深度
            if task.depth <= 2:
                # 简化分析，只使用市场和新闻
                parameters["selected_analysts"] = ["market", "news"]
            elif task.depth >= 4:
                # 深度分析，包含所有分析师
                parameters["selected_analysts"] = [
                    "market",
                    "social",
                    "news",
                    "fundamentals",
                ]

            # 运行 TradingAgents 分析
            result = await TradingService.run_analysis(
                db, task.id, task.user_id, parameters
            )

            # 更新任务结果
            await AnalysisService.update_task_result(db, task.id, result)

            # 推送完成消息
            await websocket_manager.broadcast_to_user(
                str(task.user_id),
                {
                    "type": "analysis_complete",
                    "task_id": str(task.id),
                    "progress": 100,
                    "stage": "completed",
                    "message": "分析完成",
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                },
            )

        except Exception as e:
            # 更新错误状态
            await AnalysisService.update_task_status(
                db, task.id, status="failed", error_message=str(e)
            )

            # 推送错误消息
            await websocket_manager.broadcast_to_user(
                str(task.user_id),
                {
                    "type": "analysis_failed",
                    "task_id": str(task.id),
                    "progress": 0,
                    "stage": "failed",
                    "message": f"分析失败: {str(e)}",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                },
            )
