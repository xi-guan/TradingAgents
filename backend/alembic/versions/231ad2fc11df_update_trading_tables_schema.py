"""update_trading_tables_schema

Revision ID: 231ad2fc11df
Revises: 74407c042167
Create Date: 2025-11-19 00:43:35.731369

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '231ad2fc11df'
down_revision = '74407c042167'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Positions table updates
    # Drop old foreign key and indexes
    op.drop_index('ix_positions_account_stock', table_name='positions')
    op.drop_constraint('positions_stock_id_fkey', 'positions', type_='foreignkey')

    # Drop old columns
    op.drop_column('positions', 'stock_id')
    op.drop_column('positions', 'market_value')
    op.drop_column('positions', 'profit_loss')
    op.drop_column('positions', 'profit_loss_rate')

    # Add new columns
    op.add_column('positions', sa.Column('symbol', sa.String(20), nullable=False, server_default=''))
    op.add_column('positions', sa.Column('market', sa.String(10), nullable=False, server_default='CN'))
    op.add_column('positions', sa.Column('unrealized_pnl', sa.Numeric(20, 4)))

    # Remove server defaults after adding columns
    op.alter_column('positions', 'symbol', server_default=None)
    op.alter_column('positions', 'market', server_default=None)

    # Add new index
    op.create_index('idx_position_account_symbol', 'positions', ['account_id', 'symbol', 'market'])

    # Orders table updates
    # Drop old foreign key
    op.drop_constraint('orders_stock_id_fkey', 'orders', type_='foreignkey')

    # Drop old columns
    op.drop_column('orders', 'stock_id')
    op.drop_column('orders', 'commission')
    op.drop_column('orders', 'notes')
    op.drop_column('orders', 'cancelled_at')

    # Add new columns
    op.add_column('orders', sa.Column('symbol', sa.String(20), nullable=False, server_default=''))
    op.add_column('orders', sa.Column('market', sa.String(10), nullable=False, server_default='CN'))

    # Remove server defaults
    op.alter_column('orders', 'symbol', server_default=None)
    op.alter_column('orders', 'market', server_default=None)

    # Drop old index and add new one
    op.drop_index('ix_orders_created_at', table_name='orders')
    op.create_index('idx_order_account_created', 'orders', ['account_id', 'created_at'])
    op.create_index('idx_order_status', 'orders', ['status', 'created_at'])


def downgrade() -> None:
    # Reverse orders table changes
    op.drop_index('idx_order_status', table_name='orders')
    op.drop_index('idx_order_account_created', table_name='orders')
    op.create_index('ix_orders_created_at', 'orders', ['created_at'])

    op.drop_column('orders', 'market')
    op.drop_column('orders', 'symbol')

    op.add_column('orders', sa.Column('cancelled_at', sa.DateTime(timezone=True)))
    op.add_column('orders', sa.Column('notes', sa.Text()))
    op.add_column('orders', sa.Column('commission', sa.Numeric(20, 2), server_default='0', nullable=False))
    op.add_column('orders', sa.Column('stock_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False))

    op.create_foreign_key('orders_stock_id_fkey', 'orders', 'stocks', ['stock_id'], ['id'], ondelete='CASCADE')

    # Reverse positions table changes
    op.drop_index('idx_position_account_symbol', table_name='positions')

    op.drop_column('positions', 'unrealized_pnl')
    op.drop_column('positions', 'market')
    op.drop_column('positions', 'symbol')

    op.add_column('positions', sa.Column('profit_loss_rate', sa.Numeric(10, 4)))
    op.add_column('positions', sa.Column('profit_loss', sa.Numeric(20, 2)))
    op.add_column('positions', sa.Column('market_value', sa.Numeric(20, 2)))
    op.add_column('positions', sa.Column('stock_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False))

    op.create_foreign_key('positions_stock_id_fkey', 'positions', 'stocks', ['stock_id'], ['id'], ondelete='CASCADE')
    op.create_index('ix_positions_account_stock', 'positions', ['account_id', 'stock_id'], unique=True)
