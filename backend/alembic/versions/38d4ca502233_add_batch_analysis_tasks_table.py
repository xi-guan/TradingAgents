"""add_batch_analysis_tasks_table

Revision ID: 38d4ca502233
Revises: 803516288866
Create Date: 2025-11-19 00:53:06.350058

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '38d4ca502233'
down_revision = '803516288866'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create batch_analysis_tasks table
    op.create_table(
        'batch_analysis_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('parameters', postgresql.JSON, nullable=False),
        sa.Column('status', sa.String(20), server_default='pending', nullable=False),
        sa.Column('total_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('completed_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('failed_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('subtask_ids', postgresql.JSON),
        sa.Column('error', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True)),
        sa.Column('completed_at', sa.DateTime(timezone=True)),

        # Foreign keys
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create indexes
    op.create_index('ix_batch_analysis_tasks_user_id', 'batch_analysis_tasks', ['user_id'])
    op.create_index('ix_batch_analysis_tasks_status', 'batch_analysis_tasks', ['status'])
    op.create_index('ix_batch_analysis_tasks_created_at', 'batch_analysis_tasks', ['created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_batch_analysis_tasks_created_at', table_name='batch_analysis_tasks')
    op.drop_index('ix_batch_analysis_tasks_status', table_name='batch_analysis_tasks')
    op.drop_index('ix_batch_analysis_tasks_user_id', table_name='batch_analysis_tasks')

    # Drop table
    op.drop_table('batch_analysis_tasks')
