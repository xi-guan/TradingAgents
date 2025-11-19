"""Trading analysis service - 包装 TradingAgents 核心逻辑"""

import asyncio
import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.websocket_manager import websocket_manager
from app.models.analysis import AnalysisTask
from app.services.analysis_service import AnalysisService


class TradingService:
    """Trading analysis service wrapper"""

    @staticmethod
    def _create_config(parameters: dict[str, Any]) -> dict[str, Any]:
        """
        创建 TradingAgents 配置

        Args:
            parameters: 分析参数

        Returns:
            配置字典
        """
        # 获取项目根目录
        project_dir = Path(__file__).parents[3]  # backend/app/services -> TradingAgents

        config = {
            # 项目目录
            "project_dir": str(project_dir),
            # LLM 配置
            "llm_provider": parameters.get("llm_provider", "openai"),
            "deep_think_llm": parameters.get("deep_think_llm", settings.openai_model_name),
            "quick_think_llm": parameters.get("quick_think_llm", settings.openai_model_name),
            "backend_url": parameters.get("backend_url", settings.openai_base_url),
            # 数据配置
            "alpha_vantage_key": settings.alpha_vantage_api_key,
            # 分析师配置
            "selected_analysts": parameters.get(
                "selected_analysts", ["market", "social", "news", "fundamentals"]
            ),
        }

        return config

    @staticmethod
    async def run_analysis(
        db: AsyncSession, task_id: UUID, user_id: UUID, parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """
        运行交易分析

        Args:
            db: 数据库会话
            task_id: 任务 ID
            user_id: 用户 ID
            parameters: 分析参数，包含：
                - company_name: 公司名称/股票代码
                - trade_date: 交易日期（可选，默认今天）
                - selected_analysts: 选择的分析师（可选）
                - llm_provider: LLM 提供商（可选）
                - deep_think_llm: 深度思考模型（可选）
                - quick_think_llm: 快速思考模型（可选）

        Returns:
            分析结果字典
        """
        # 更新任务状态
        await AnalysisService.update_task_progress(
            db, task_id, progress=10, status="running"
        )

        # 发送 WebSocket 通知
        await websocket_manager.broadcast_to_user(
            str(user_id),
            {
                "type": "analysis_progress",
                "task_id": str(task_id),
                "progress": 10,
                "status": "正在初始化分析引擎...",
            },
        )

        try:
            # 在线程池中运行 TradingAgents
            result = await asyncio.to_thread(
                TradingService._run_trading_agents_sync, db, task_id, user_id, parameters
            )

            # 更新任务完成状态
            await AnalysisService.update_task_progress(
                db, task_id, progress=100, status="completed"
            )

            await websocket_manager.broadcast_to_user(
                str(user_id),
                {
                    "type": "analysis_complete",
                    "task_id": str(task_id),
                    "result": result,
                },
            )

            return result

        except Exception as e:
            # 更新任务失败状态
            await AnalysisService.update_task_status(
                db, task_id, status="failed", error_message=str(e)
            )

            await websocket_manager.broadcast_to_user(
                str(user_id),
                {
                    "type": "analysis_failed",
                    "task_id": str(task_id),
                    "error": str(e),
                },
            )

            raise

    @staticmethod
    def _run_trading_agents_sync(
        db: AsyncSession, task_id: UUID, user_id: UUID, parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """
        同步运行 TradingAgents（在线程池中调用）

        Args:
            db: 数据库会话
            task_id: 任务 ID
            user_id: 用户 ID
            parameters: 分析参数

        Returns:
            分析结果
        """
        # 延迟导入，避免启动时就加载所有依赖
        try:
            from tradingagents.graph.trading_graph import TradingAgentsGraph
        except ImportError as e:
            return {
                "error": f"TradingAgents 未安装或配置错误: {str(e)}",
                "status": "failed",
            }

        # 创建配置
        config = TradingService._create_config(parameters)

        # 获取参数
        company_name = parameters.get("company_name")
        trade_date = parameters.get("trade_date")

        if not company_name:
            return {"error": "缺少 company_name 参数", "status": "failed"}

        # 转换日期
        if trade_date:
            if isinstance(trade_date, str):
                trade_date = datetime.fromisoformat(trade_date).date()
        else:
            trade_date = date.today()

        # 创建 TradingAgentsGraph 实例
        selected_analysts = parameters.get(
            "selected_analysts", ["market", "social", "news", "fundamentals"]
        )

        graph = TradingAgentsGraph(
            selected_analysts=selected_analysts, debug=False, config=config
        )

        # 运行分析
        final_state, processed_signal = graph.propagate(company_name, trade_date)

        # 提取结果
        result = {
            "company_of_interest": final_state.get("company_of_interest"),
            "trade_date": str(trade_date),
            "final_trade_decision": final_state.get("final_trade_decision"),
            "processed_signal": processed_signal,
            "analyst_reports": {},
            "debate_results": {},
        }

        # 提取分析师报告
        if "market_analyst" in final_state:
            result["analyst_reports"]["market"] = final_state["market_analyst"]

        if "social_analyst" in final_state:
            result["analyst_reports"]["social"] = final_state["social_analyst"]

        if "news_analyst" in final_state:
            result["analyst_reports"]["news"] = final_state["news_analyst"]

        if "fundamentals_analyst" in final_state:
            result["analyst_reports"]["fundamentals"] = final_state["fundamentals_analyst"]

        # 提取辩论结果
        if "investment_debate_outcome" in final_state:
            result["debate_results"]["investment"] = final_state[
                "investment_debate_outcome"
            ]

        if "risk_debate_outcome" in final_state:
            result["debate_results"]["risk"] = final_state["risk_debate_outcome"]

        # 提取trader决策
        if "trader_decision" in final_state:
            result["trader_decision"] = final_state["trader_decision"]

        return result

    @staticmethod
    async def get_reflection(
        db: AsyncSession, task_id: UUID, company_name: str
    ) -> dict[str, Any]:
        """
        获取反思分析

        Args:
            db: 数据库会话
            task_id: 任务 ID
            company_name: 公司名称

        Returns:
            反思结果
        """
        # TODO: 实现反思功能
        # 这需要保持 graph 实例的状态，可能需要使用缓存
        return {
            "error": "反思功能待实现",
            "status": "not_implemented",
        }
