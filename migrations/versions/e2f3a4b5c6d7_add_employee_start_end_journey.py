"""add employee start_time and end_time (jornada)

Revision ID: e2f3a4b5c6d7
Revises: c1d2e3f4a5b6
Create Date: 2026-04-03 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'e2f3a4b5c6d7'
down_revision: Union[str, Sequence[str], None] = 'c1d2e3f4a5b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'employee',
        sa.Column(
            'start_time',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("'1970-01-01 08:30:00+00'::timestamptz"),
        ),
    )
    op.add_column(
        'employee',
        sa.Column(
            'end_time',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("'1970-01-01 21:00:00+00'::timestamptz"),
        ),
    )
    op.alter_column('employee', 'start_time', server_default=None)
    op.alter_column('employee', 'end_time', server_default=None)


def downgrade() -> None:
    op.drop_column('employee', 'end_time')
    op.drop_column('employee', 'start_time')
