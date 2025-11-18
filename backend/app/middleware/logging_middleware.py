"""日志中间件"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        # 记录请求开始时间
        start_time = time.time()

        # 生成请求 ID
        request_id = request.headers.get("X-Request-ID", f"{time.time()}")
        request.state.request_id = request_id

        # 记录请求信息
        logger.info(
            f"Request started: {request.method} {request.url.path} "
            f"[{request_id}]"
        )

        # 执行请求
        response = await call_next(request)

        # 计算处理时间
        process_time = time.time() - start_time

        # 添加响应头
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)

        # 记录响应信息
        logger.info(
            f"Request completed: {request.method} {request.url.path} "
            f"[{request_id}] - Status: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )

        return response
