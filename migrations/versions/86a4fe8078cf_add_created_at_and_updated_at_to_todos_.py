"""Add created_at and updated_at to TODOS table

Revision ID: 86a4fe8078cf
Revises: 58963f4e6b4a
Create Date: 2024-07-23 22:44:02.596418

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '86a4fe8078cf'
down_revision: Union[str, None] = '58963f4e6b4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('todos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('todos', 'updated_at')
    op.drop_column('todos', 'created_at')
    # ### end Alembic commands ###
