"""add_task_id_and_status_to_summary

Revision ID: c9e6e7dbbbfc
Revises: b885c2d2ecb7
Create Date: 2025-10-17 16:20:24.659423

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9e6e7dbbbfc'
down_revision: Union[str, None] = 'b885c2d2ecb7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add task_id column
    op.add_column('summaries', sa.Column('task_id', sa.String(length=36), nullable=True))
    
    # Add status column - make it nullable for SQLite compatibility
    op.add_column('summaries', sa.Column('status', sa.String(length=20), nullable=True))
    
    # Create indexes
    op.create_index(op.f('ix_summaries_task_id'), 'summaries', ['task_id'], unique=False)
    
    # Set default values for existing records
    op.execute("UPDATE summaries SET status = 'completed' WHERE is_successful = true")
    op.execute("UPDATE summaries SET status = 'failed' WHERE is_successful = false")


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_summaries_task_id'), table_name='summaries')
    
    # Drop columns
    op.drop_column('summaries', 'status')
    op.drop_column('summaries', 'task_id')
