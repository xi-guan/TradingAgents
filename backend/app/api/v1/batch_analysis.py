"""批量分析 API 路由"""

import asyncio
from uuid import UUID

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import CurrentUser
from app.schemas.batch_analysis import (
    BatchAnalysisCreate,
    BatchAnalysisResponse,
    BatchAnalysisProgress,
)
from app.services.batch_analysis_service import BatchAnalysisService

router = APIRouter()


@router.post("", response_model=BatchAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def create_batch_analysis(
    batch_create: BatchAnalysisCreate,
    background_tasks: BackgroundTasks,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    创建批量分析任务

    支持两种方式:
    1. 直接指定 symbols 和 markets 列表
    2. 从自选股分组创建 (from_watchlist_group)
    """
    # 创建批量任务
    batch_task = await BatchAnalysisService.create_batch_task(
        db, current_user.id, batch_create
    )

    # 在后台执行批量分析
    background_tasks.add_task(
        BatchAnalysisService.execute_batch_task,
        db,
        batch_task.id,
        current_user.id,
    )

    # 计算进度百分比
    progress_percent = 0.0
    if batch_task.total_count > 0:
        progress_percent = (batch_task.completed_count / batch_task.total_count) * 100

    return BatchAnalysisResponse(
        id=batch_task.id,
        user_id=batch_task.user_id,
        name=batch_task.name,
        parameters=batch_task.parameters,
        status=batch_task.status,
        total_count=batch_task.total_count,
        completed_count=batch_task.completed_count,
        failed_count=batch_task.failed_count,
        subtask_ids=batch_task.subtask_ids,
        error=batch_task.error,
        created_at=batch_task.created_at,
        started_at=batch_task.started_at,
        completed_at=batch_task.completed_at,
        progress_percent=progress_percent,
    )


@router.get("", response_model=list[BatchAnalysisResponse])
async def get_batch_tasks(
    current_user: CurrentUser,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """获取批量分析任务列表"""
    batch_tasks = await BatchAnalysisService.get_user_batch_tasks(
        db, current_user.id, limit
    )

    # 转换为响应模型
    responses = []
    for task in batch_tasks:
        progress_percent = 0.0
        if task.total_count > 0:
            progress_percent = (task.completed_count / task.total_count) * 100

        responses.append(
            BatchAnalysisResponse(
                id=task.id,
                user_id=task.user_id,
                name=task.name,
                parameters=task.parameters,
                status=task.status,
                total_count=task.total_count,
                completed_count=task.completed_count,
                failed_count=task.failed_count,
                subtask_ids=task.subtask_ids,
                error=task.error,
                created_at=task.created_at,
                started_at=task.started_at,
                completed_at=task.completed_at,
                progress_percent=progress_percent,
            )
        )

    return responses


@router.get("/{task_id}", response_model=BatchAnalysisResponse)
async def get_batch_task(
    task_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """获取批量分析任务详情"""
    batch_task = await BatchAnalysisService.get_batch_task(db, task_id)

    if not batch_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch task not found",
        )

    # 验证权限
    if batch_task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this batch task",
        )

    # 计算进度
    progress_percent = 0.0
    if batch_task.total_count > 0:
        progress_percent = (batch_task.completed_count / batch_task.total_count) * 100

    return BatchAnalysisResponse(
        id=batch_task.id,
        user_id=batch_task.user_id,
        name=batch_task.name,
        parameters=batch_task.parameters,
        status=batch_task.status,
        total_count=batch_task.total_count,
        completed_count=batch_task.completed_count,
        failed_count=batch_task.failed_count,
        subtask_ids=batch_task.subtask_ids,
        error=batch_task.error,
        created_at=batch_task.created_at,
        started_at=batch_task.started_at,
        completed_at=batch_task.completed_at,
        progress_percent=progress_percent,
    )


@router.get("/{task_id}/progress", response_model=BatchAnalysisProgress)
async def get_batch_progress(
    task_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """获取批量分析进度"""
    batch_task = await BatchAnalysisService.get_batch_task(db, task_id)

    if not batch_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch task not found",
        )

    # 验证权限
    if batch_task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this batch task",
        )

    # 计算进度
    progress_percent = 0.0
    if batch_task.total_count > 0:
        progress_percent = (batch_task.completed_count / batch_task.total_count) * 100

    # 获取当前正在分析的股票（如果有）
    current_symbol = None
    if batch_task.status == "running" and batch_task.completed_count < batch_task.total_count:
        symbols = batch_task.parameters.get("symbols", [])
        if batch_task.completed_count < len(symbols):
            current_symbol = symbols[batch_task.completed_count]

    return BatchAnalysisProgress(
        task_id=batch_task.id,
        status=batch_task.status,
        total_count=batch_task.total_count,
        completed_count=batch_task.completed_count,
        failed_count=batch_task.failed_count,
        progress_percent=progress_percent,
        current_symbol=current_symbol,
    )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_batch_task(
    task_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """取消批量分析任务"""
    await BatchAnalysisService.cancel_batch_task(db, task_id, current_user.id)
