"""Initial schema with all models

Revision ID: 74407c042167
Revises:
Create Date: 2025-11-19 00:04:55.003823

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '74407c042167'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 启用 UUID 扩展
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # 创建 users 表
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('username', sa.String(100), nullable=False, unique=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(200)),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('is_superuser', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('preferred_language', sa.String(10), server_default='zh_CN', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_username', 'users', ['username'])

    # 创建 stocks 表
    op.create_table(
        'stocks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('symbol', sa.String(20), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('market', sa.String(10), nullable=False),
        sa.Column('sector', sa.String(100)),
        sa.Column('industry', sa.String(100)),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_stocks_symbol_market', 'stocks', ['symbol', 'market'], unique=True)
    op.create_index('ix_stocks_market', 'stocks', ['market'])

    # 创建 stock_quotes 表
    op.create_table(
        'stock_quotes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('stock_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('stocks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('open', sa.Numeric(20, 4)),
        sa.Column('high', sa.Numeric(20, 4)),
        sa.Column('low', sa.Numeric(20, 4)),
        sa.Column('close', sa.Numeric(20, 4), nullable=False),
        sa.Column('volume', sa.BigInteger()),
        sa.Column('prev_close', sa.Numeric(20, 4)),
        sa.Column('change', sa.Numeric(20, 4)),
        sa.Column('change_percent', sa.Numeric(10, 4)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_stock_quotes_stock_id', 'stock_quotes', ['stock_id'])
    op.create_index('ix_stock_quotes_timestamp', 'stock_quotes', ['timestamp'])

    # 创建 stock_history 表（时序数据）
    op.create_table(
        'stock_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('stock_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('stocks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('open', sa.Numeric(20, 4)),
        sa.Column('high', sa.Numeric(20, 4)),
        sa.Column('low', sa.Numeric(20, 4)),
        sa.Column('close', sa.Numeric(20, 4), nullable=False),
        sa.Column('volume', sa.BigInteger()),
        sa.Column('adj_close', sa.Numeric(20, 4)),
        sa.Column('interval', sa.String(10), server_default='1d', nullable=False),
    )
    op.create_index('ix_stock_history_stock_timestamp', 'stock_history', ['stock_id', 'timestamp', 'interval'], unique=True)
    op.create_index('ix_stock_history_timestamp', 'stock_history', ['timestamp'])

    # 将 stock_history 转换为 TimescaleDB 超表（hypertable）
    op.execute("""
        SELECT create_hypertable('stock_history', 'timestamp',
                                 if_not_exists => TRUE,
                                 migrate_data => TRUE);
    """)

    # 创建 analysis_tasks 表
    op.create_table(
        'analysis_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('task_type', sa.String(50), nullable=False),
        sa.Column('parameters', postgresql.JSON(), nullable=False),
        sa.Column('status', sa.String(20), server_default='pending', nullable=False),
        sa.Column('progress', sa.Integer(), server_default='0', nullable=False),
        sa.Column('result', postgresql.JSON()),
        sa.Column('error_message', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True)),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
    )
    op.create_index('ix_analysis_tasks_user_id', 'analysis_tasks', ['user_id'])
    op.create_index('ix_analysis_tasks_status', 'analysis_tasks', ['status'])
    op.create_index('ix_analysis_tasks_created_at', 'analysis_tasks', ['created_at'])

    # 创建 trading_accounts 表
    op.create_table(
        'trading_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('account_type', sa.String(20), server_default='paper', nullable=False),
        sa.Column('market', sa.String(10), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False),
        sa.Column('initial_capital', sa.Numeric(20, 2), nullable=False),
        sa.Column('cash_balance', sa.Numeric(20, 2), nullable=False),
        sa.Column('total_value', sa.Numeric(20, 2), nullable=False),
        sa.Column('total_profit_loss', sa.Numeric(20, 2), server_default='0', nullable=False),
        sa.Column('total_return_rate', sa.Numeric(10, 4), server_default='0', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_trading_accounts_user_id', 'trading_accounts', ['user_id'])

    # 创建 positions 表
    op.create_table(
        'positions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('trading_accounts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('stock_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('stocks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('avg_cost', sa.Numeric(20, 4), nullable=False),
        sa.Column('current_price', sa.Numeric(20, 4)),
        sa.Column('market_value', sa.Numeric(20, 2)),
        sa.Column('profit_loss', sa.Numeric(20, 2)),
        sa.Column('profit_loss_rate', sa.Numeric(10, 4)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_positions_account_id', 'positions', ['account_id'])
    op.create_index('ix_positions_account_stock', 'positions', ['account_id', 'stock_id'], unique=True)

    # 创建 orders 表
    op.create_table(
        'orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('trading_accounts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('stock_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('stocks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('order_type', sa.String(20), nullable=False),
        sa.Column('side', sa.String(10), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('price', sa.Numeric(20, 4)),
        sa.Column('status', sa.String(20), server_default='pending', nullable=False),
        sa.Column('filled_quantity', sa.Integer(), server_default='0', nullable=False),
        sa.Column('filled_price', sa.Numeric(20, 4)),
        sa.Column('commission', sa.Numeric(20, 2), server_default='0', nullable=False),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('filled_at', sa.DateTime(timezone=True)),
        sa.Column('cancelled_at', sa.DateTime(timezone=True)),
    )
    op.create_index('ix_orders_account_id', 'orders', ['account_id'])
    op.create_index('ix_orders_status', 'orders', ['status'])
    op.create_index('ix_orders_created_at', 'orders', ['created_at'])


def downgrade() -> None:
    # 删除表（按照依赖关系的反向顺序）
    op.drop_table('orders')
    op.drop_table('positions')
    op.drop_table('trading_accounts')
    op.drop_table('analysis_tasks')
    op.drop_table('stock_history')
    op.drop_table('stock_quotes')
    op.drop_table('stocks')
    op.drop_table('users')

    # 删除 UUID 扩展
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
