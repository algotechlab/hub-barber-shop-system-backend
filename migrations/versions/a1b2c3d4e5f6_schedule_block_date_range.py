"""schedule_block date range and time columns

Revision ID: a1b2c3d4e5f6
Revises: f7e8d9c0b1a2
Create Date: 2026-04-22 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f7e8d9c0b1a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'schedule_block',
        sa.Column('start_date', sa.Date(), nullable=True),
    )
    op.add_column(
        'schedule_block',
        sa.Column('end_date', sa.Date(), nullable=True),
    )
    op.execute(
        sa.text(
            """
            UPDATE schedule_block
            SET
                start_date = start_time::date,
                end_date = end_time::date
            """
        )
    )
    op.alter_column('schedule_block', 'start_date', nullable=False)
    op.alter_column('schedule_block', 'end_date', nullable=False)
    op.alter_column(
        'schedule_block',
        'start_time',
        existing_type=sa.DateTime(),
        type_=sa.Time(),
        postgresql_using='start_time::time',
        existing_nullable=False,
    )
    op.alter_column(
        'schedule_block',
        'end_time',
        existing_type=sa.DateTime(),
        type_=sa.Time(),
        postgresql_using='end_time::time',
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        'schedule_block',
        'start_time',
        existing_type=sa.Time(),
        type_=sa.DateTime(),
        postgresql_using='(start_date + start_time)::timestamp',
        existing_nullable=False,
    )
    op.alter_column(
        'schedule_block',
        'end_time',
        existing_type=sa.Time(),
        type_=sa.DateTime(),
        postgresql_using='(end_date + end_time)::timestamp',
        existing_nullable=False,
    )
    op.drop_column('schedule_block', 'end_date')
    op.drop_column('schedule_block', 'start_date')
