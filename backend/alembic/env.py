"""Alembic 环境配置"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import asyncio
from sqlalchemy.ext.asyncio import AsyncEngine

# 导入配置
from app.config import settings
from app.core.database import Base

# 导入所有模型（确保所有表都被创建）
from app.models import (
    User,
    Stock,
    StockQuote,
    StockHistory,
    AnalysisTask,
    TradingAccount,
    Position,
    Order,
)

# this is the Alembic Config object
config = context.config

# 设置数据库 URL
config.set_main_option("sqlalchemy.url", settings.database_url.replace("+asyncpg", ""))

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    from sqlalchemy.ext.asyncio import create_async_engine

    connectable = create_async_engine(
        settings.database_url,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
