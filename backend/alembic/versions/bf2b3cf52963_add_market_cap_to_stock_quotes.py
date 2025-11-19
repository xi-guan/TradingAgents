"""add_market_cap_to_stock_quotes

Revision ID: bf2b3cf52963
Revises: 3b6284f6e0fe
Create Date: 2025-11-19 11:37:29.669041

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bf2b3cf52963'
down_revision = '3b6284f6e0fe'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add market_cap column to stock_quotes table
    op.add_column('stock_quotes', sa.Column('market_cap', sa.Numeric(20, 2), nullable=True))


def downgrade() -> None:
    # Remove market_cap column
    op.drop_column('stock_quotes', 'market_cap')
