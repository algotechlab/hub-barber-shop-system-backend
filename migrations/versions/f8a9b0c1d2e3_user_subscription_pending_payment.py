"""user subscription pending payment status and unique pending per plan

Revision ID: f8a9b0c1d2e3
Revises: e2f3a4b5c6d8
Create Date: 2026-04-24

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'f8a9b0c1d2e3'
down_revision: Union[str, Sequence[str], None] = 'e2f3a4b5c6d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ADD VALUE não pode estar na mesma transação que um comando que use o novo
    # membro do enum (ex.: predicado do índice). Exige commit antes — autocommit.
    with op.get_context().autocommit_block():
        op.execute(
            sa.text(
                "ALTER TYPE user_subscription_status_enum ADD VALUE 'PENDING_PAYMENT'"
            )
        )
    op.create_index(
        'uq_user_subscription_one_pending_per_plan',
        'user_subscription',
        ['user_id', 'subscription_plan_id'],
        unique=True,
        postgresql_where=sa.text("status = 'PENDING_PAYMENT' AND is_deleted IS FALSE"),
    )


def downgrade() -> None:
    op.drop_index(
        'uq_user_subscription_one_pending_per_plan', table_name='user_subscription'
    )
