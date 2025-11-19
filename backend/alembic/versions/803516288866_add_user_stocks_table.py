"""add_user_stocks_table

Revision ID: 803516288866
Revises: 231ad2fc11df
Create Date: 2025-11-19 00:50:07.748276

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '803516288866'
down_revision = '231ad2fc11df'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_stocks table
    op.create_table(
        'user_stocks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('stock_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('group_name', sa.String(50)),
        sa.Column('notes', sa.String(500)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),

        # Foreign keys
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], ondelete='CASCADE'),

        # Unique constraint
        sa.UniqueConstraint('user_id', 'stock_id', name='uq_user_stock'),
    )

    # Create indexes
    op.create_index('ix_user_stocks_user_id', 'user_stocks', ['user_id'])
    op.create_index('ix_user_stocks_stock_id', 'user_stocks', ['stock_id'])
    op.create_index('ix_user_stock_user_group', 'user_stocks', ['user_id', 'group_name'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_user_stock_user_group', table_name='user_stocks')
    op.drop_index('ix_user_stocks_stock_id', table_name='user_stocks')
    op.drop_index('ix_user_stocks_user_id', table_name='user_stocks')

    # Drop table
    op.drop_table('user_stocks')
