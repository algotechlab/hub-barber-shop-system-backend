"""alter schedule.service_id to UUID[]

Revision ID: 6a2d3c4e5f6g
Revises: 9a7a0f2b1c3d
Create Date: 2026-03-18 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6a2d3c4e5f6g'
down_revision: Union[str, Sequence[str], None] = '9a7a0f2b1c3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # A coluna vira array, então a FK original precisa ser removida.
    op.drop_constraint(
        op.f('schedule_service_id_fkey'),
        'schedule',
        type_='foreignkey',
    )

    op.alter_column(
        'schedule',
        'service_id',
        existing_type=sa.Uuid(),
        type_=postgresql.ARRAY(sa.Uuid()),
        existing_nullable=False,
        nullable=False,
        postgresql_using='ARRAY[service_id]',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'schedule',
        'service_id',
        existing_type=postgresql.ARRAY(sa.Uuid()),
        type_=sa.Uuid(),
        existing_nullable=False,
        nullable=False,
        postgresql_using='service_id[1]',
    )

    # Recria a FK para o modo antigo (1 serviço por agendamento).
    op.create_foreign_key(
        op.f('schedule_service_id_fkey'),
        'schedule',
        'service',
        ['service_id'],
        ['id'],
    )
