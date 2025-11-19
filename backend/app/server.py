"""服务器启动入口

使用方式:
    uv run python -m app.server
    或
    python -m app.server
"""

import uvicorn
from app.config import settings


def main():
    """启动服务器"""
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8005,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
