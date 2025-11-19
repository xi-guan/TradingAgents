"""add_news_and_financials_tables

Revision ID: 3b6284f6e0fe
Revises: 38d4ca502233
Create Date: 2025-11-19 09:18:03.561092

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '3b6284f6e0fe'
down_revision = '38d4ca502233'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create news_articles table
    op.create_table(
        'news_articles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('symbol', sa.String(20), nullable=False),
        sa.Column('market', sa.String(10), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('summary', sa.Text()),
        sa.Column('content', sa.Text()),
        sa.Column('url', sa.String(1000), nullable=False),
        sa.Column('source', sa.String(100), nullable=False),
        sa.Column('author', sa.String(200)),
        sa.Column('sentiment', sa.String(20)),
        sa.Column('sentiment_score', sa.Float()),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # Create indexes for news_articles
    op.create_index('ix_news_articles_symbol', 'news_articles', ['symbol'])
    op.create_index('ix_news_articles_market', 'news_articles', ['market'])
    op.create_index('ix_news_articles_published_at', 'news_articles', ['published_at'])
    op.create_index('ix_news_url_unique', 'news_articles', ['url'], unique=True)
    op.create_index('ix_news_symbol_published', 'news_articles', ['symbol', 'market', 'published_at'])

    # Create financial_statements table
    op.create_table(
        'financial_statements',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('symbol', sa.String(20), nullable=False),
        sa.Column('market', sa.String(10), nullable=False),
        sa.Column('statement_type', sa.String(20), nullable=False),
        sa.Column('period_type', sa.String(20), nullable=False),
        sa.Column('fiscal_year', sa.Integer(), nullable=False),
        sa.Column('fiscal_quarter', sa.Integer()),
        sa.Column('report_date', sa.Date(), nullable=False),
        # Income statement
        sa.Column('revenue', sa.Numeric(20, 2)),
        sa.Column('cost_of_revenue', sa.Numeric(20, 2)),
        sa.Column('gross_profit', sa.Numeric(20, 2)),
        sa.Column('operating_expenses', sa.Numeric(20, 2)),
        sa.Column('operating_income', sa.Numeric(20, 2)),
        sa.Column('net_income', sa.Numeric(20, 2)),
        sa.Column('ebitda', sa.Numeric(20, 2)),
        sa.Column('eps', sa.Numeric(10, 4)),
        # Balance sheet
        sa.Column('total_assets', sa.Numeric(20, 2)),
        sa.Column('total_liabilities', sa.Numeric(20, 2)),
        sa.Column('total_equity', sa.Numeric(20, 2)),
        sa.Column('current_assets', sa.Numeric(20, 2)),
        sa.Column('current_liabilities', sa.Numeric(20, 2)),
        sa.Column('cash_and_equivalents', sa.Numeric(20, 2)),
        # Cash flow
        sa.Column('operating_cashflow', sa.Numeric(20, 2)),
        sa.Column('investing_cashflow', sa.Numeric(20, 2)),
        sa.Column('financing_cashflow', sa.Numeric(20, 2)),
        sa.Column('free_cashflow', sa.Numeric(20, 2)),
        # Metadata
        sa.Column('currency', sa.String(10), server_default='USD', nullable=False),
        sa.Column('source', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # Create indexes for financial_statements
    op.create_index('ix_financial_statements_symbol', 'financial_statements', ['symbol'])
    op.create_index('ix_financial_statements_market', 'financial_statements', ['market'])
    op.create_index('ix_financial_statements_report_date', 'financial_statements', ['report_date'])
    op.create_index('ix_financial_unique', 'financial_statements',
                    ['symbol', 'market', 'statement_type', 'period_type', 'fiscal_year', 'fiscal_quarter'], unique=True)
    op.create_index('ix_financial_symbol_date', 'financial_statements', ['symbol', 'market', 'report_date'])

    # Create financial_metrics table
    op.create_table(
        'financial_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('symbol', sa.String(20), nullable=False),
        sa.Column('market', sa.String(10), nullable=False),
        sa.Column('report_date', sa.Date(), nullable=False),
        sa.Column('period_type', sa.String(20), nullable=False),
        # Valuation
        sa.Column('pe_ratio', sa.Numeric(10, 2)),
        sa.Column('pb_ratio', sa.Numeric(10, 2)),
        sa.Column('ps_ratio', sa.Numeric(10, 2)),
        sa.Column('pcf_ratio', sa.Numeric(10, 2)),
        sa.Column('ev_to_ebitda', sa.Numeric(10, 2)),
        # Profitability
        sa.Column('roe', sa.Numeric(10, 4)),
        sa.Column('roa', sa.Numeric(10, 4)),
        sa.Column('gross_margin', sa.Numeric(10, 4)),
        sa.Column('operating_margin', sa.Numeric(10, 4)),
        sa.Column('net_margin', sa.Numeric(10, 4)),
        # Growth
        sa.Column('revenue_growth', sa.Numeric(10, 4)),
        sa.Column('earnings_growth', sa.Numeric(10, 4)),
        # Solvency
        sa.Column('current_ratio', sa.Numeric(10, 2)),
        sa.Column('quick_ratio', sa.Numeric(10, 2)),
        sa.Column('debt_to_equity', sa.Numeric(10, 2)),
        # Efficiency
        sa.Column('asset_turnover', sa.Numeric(10, 2)),
        sa.Column('inventory_turnover', sa.Numeric(10, 2)),
        # Metadata
        sa.Column('source', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # Create indexes for financial_metrics
    op.create_index('ix_financial_metrics_symbol', 'financial_metrics', ['symbol'])
    op.create_index('ix_financial_metrics_market', 'financial_metrics', ['market'])
    op.create_index('ix_financial_metrics_report_date', 'financial_metrics', ['report_date'])
    op.create_index('ix_metrics_unique', 'financial_metrics', ['symbol', 'market', 'report_date', 'period_type'], unique=True)
    op.create_index('ix_metrics_symbol_date', 'financial_metrics', ['symbol', 'market', 'report_date'])


def downgrade() -> None:
    # Drop financial_metrics table
    op.drop_index('ix_metrics_symbol_date', table_name='financial_metrics')
    op.drop_index('ix_metrics_unique', table_name='financial_metrics')
    op.drop_index('ix_financial_metrics_report_date', table_name='financial_metrics')
    op.drop_index('ix_financial_metrics_market', table_name='financial_metrics')
    op.drop_index('ix_financial_metrics_symbol', table_name='financial_metrics')
    op.drop_table('financial_metrics')

    # Drop financial_statements table
    op.drop_index('ix_financial_symbol_date', table_name='financial_statements')
    op.drop_index('ix_financial_unique', table_name='financial_statements')
    op.drop_index('ix_financial_statements_report_date', table_name='financial_statements')
    op.drop_index('ix_financial_statements_market', table_name='financial_statements')
    op.drop_index('ix_financial_statements_symbol', table_name='financial_statements')
    op.drop_table('financial_statements')

    # Drop news_articles table
    op.drop_index('ix_news_symbol_published', table_name='news_articles')
    op.drop_index('ix_news_url_unique', table_name='news_articles')
    op.drop_index('ix_news_articles_published_at', table_name='news_articles')
    op.drop_index('ix_news_articles_market', table_name='news_articles')
    op.drop_index('ix_news_articles_symbol', table_name='news_articles')
    op.drop_table('news_articles')
