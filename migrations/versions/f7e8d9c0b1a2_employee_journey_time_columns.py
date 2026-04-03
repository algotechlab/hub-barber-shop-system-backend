"""employee journey: store start_time/end_time as TIME only

Revision ID: f7e8d9c0b1a2
Revises: e2f3a4b5c6d7
Create Date: 2026-04-04 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'f7e8d9c0b1a2'
down_revision: Union[str, Sequence[str], None] = 'e2f3a4b5c6d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'employee',
        'start_time',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.Time(),
        postgresql_using='start_time::time',
    )
    op.alter_column(
        'employee',
        'end_time',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.Time(),
        postgresql_using='end_time::time',
    )


def downgrade() -> None:
    op.alter_column(
        'employee',
        'start_time',
        existing_type=sa.Time(),
        type_=sa.DateTime(timezone=True),
        postgresql_using=(
            "((date '1970-01-01' + start_time)::timestamp AT TIME ZONE 'UTC')"
        ),
    )
    op.alter_column(
        'employee',
        'end_time',
        existing_type=sa.Time(),
        type_=sa.DateTime(timezone=True),
        postgresql_using=(
            "((date '1970-01-01' + end_time)::timestamp AT TIME ZONE 'UTC')"
        ),
    )
