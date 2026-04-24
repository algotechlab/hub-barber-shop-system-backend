"""user_subscription payment_at and payment_method

Revision ID: a1b2c3d4e5f7
Revises: f8a9b0c1d2e3
Create Date: 2026-04-24

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = 'a1b2c3d4e5f7'
down_revision: Union[str, Sequence[str], None] = 'f8a9b0c1d2e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

payment_method_enum = postgresql.ENUM(
    'CREDIT_CARD',
    'DEBIT_CARD',
    'PIX',
    'MONEY',
    'OTHER',
    name='payment_method_enum',
    create_type=False,
)


def upgrade() -> None:
    op.add_column(
        'user_subscription',
        sa.Column('payment_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        'user_subscription',
        sa.Column('payment_method', payment_method_enum, nullable=True),
    )


def downgrade() -> None:
    op.drop_column('user_subscription', 'payment_method')
    op.drop_column('user_subscription', 'payment_at')
