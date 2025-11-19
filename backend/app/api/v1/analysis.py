"""分析任务 API"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies import CurrentUser
from app.schemas.analysis import (
    AnalysisTaskCreate,
    AnalysisTaskResponse,
)
from app.services.analysis_service import AnalysisService
from app.tasks.analysis_tasks import run_analysis_task

router = APIRouter()


@router.post("/start", response_model=AnalysisTaskResponse)
async def start_analysis(
    task_create: AnalysisTaskCreate,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    """开始分析任务"""
    # 创建任务
    task = await AnalysisService.create_task(db, str(current_user.id), task_create)

    # 添加后台任务
    background_tasks.add_task(run_analysis_task, str(task.id))

    return AnalysisTaskResponse.model_validate(task)


@router.get("/{task_id}", response_model=AnalysisTaskResponse)
async def get_analysis_task(
    task_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    """获取分析任务"""
    task = await AnalysisService.get_task(db, task_id, str(current_user.id))

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return AnalysisTaskResponse.model_validate(task)


@router.get("/history", response_model=list[AnalysisTaskResponse])
async def get_analysis_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    """获取分析历史"""
    tasks = await AnalysisService.get_user_tasks(db, str(current_user.id), skip, limit)

    return [AnalysisTaskResponse.model_validate(task) for task in tasks]


@router.delete("/{task_id}")
async def delete_analysis_task(
    task_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    """删除分析任务"""
    success = await AnalysisService.delete_task(db, task_id, str(current_user.id))

    if not success:
        raise HTTPException(status_code=404, detail="任务不存在")

    return {"message": "任务已删除"}
