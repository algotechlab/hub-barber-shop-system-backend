"""add service_id uuid array to schedule_finance

Revision ID: b7c8d9e0f1a2
Revises: 6a2d3c4e5f6g
Create Date: 2026-03-18 12:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b7c8d9e0f1a2'
down_revision: Union[str, Sequence[str], None] = '6a2d3c4e5f6g'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'schedule_finance',
        sa.Column('service_id', postgresql.ARRAY(sa.Uuid()), nullable=True),
    )
    op.execute(
        """
        UPDATE schedule_finance sf
        SET service_id = s.service_id
        FROM schedule s
        WHERE s.id = sf.schedule_id
        """
    )
    op.alter_column('schedule_finance', 'service_id', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('schedule_finance', 'service_id')
