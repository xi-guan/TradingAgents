"""错误处理中间件"""

import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


async def error_handler_middleware(request: Request, call_next):
    """全局错误处理中间件"""
    try:
        response = await call_next(request)
        return response

    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "database_error",
                "message": "数据库错误",
                "detail": str(e) if request.app.debug else None
            }
        )

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "validation_error",
                "message": "参数错误",
                "detail": str(e)
            }
        )

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "internal_server_error",
                "message": "服务器内部错误",
                "detail": str(e) if request.app.debug else None
            }
        )
