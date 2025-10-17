"""rename_model_used_to_model_name

Revision ID: b885c2d2ecb7
Revises: 87025a140fca
Create Date: 2025-10-17 10:37:51.994710

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b885c2d2ecb7'
down_revision: Union[str, None] = '87025a140fca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column('summaries', 'model_used', new_column_name='model_name')

def downgrade():
    op.alter_column('summaries', 'model_name', new_column_name='model_used')
