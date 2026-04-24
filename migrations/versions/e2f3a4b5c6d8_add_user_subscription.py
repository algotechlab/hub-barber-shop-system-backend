"""add user_subscription and enum status

Revision ID: e2f3a4b5c6d8
Revises: d1e2f3a4b5c7
Create Date: 2026-04-23

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = 'e2f3a4b5c6d8'
down_revision: Union[str, Sequence[str], None] = 'd1e2f3a4b5c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _enum_values() -> list[str]:
    return ['ACTIVE', 'CANCELED', 'EXPIRED']


user_subscription_status_enum = postgresql.ENUM(
    *_enum_values(),
    name='user_subscription_status_enum',
    create_type=False,
)


def upgrade() -> None:
    user_subscription_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'user_subscription',
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('subscription_plan_id', sa.Uuid(), nullable=False),
        sa.Column('company_id', sa.Uuid(), nullable=False),
        sa.Column('status', user_subscription_status_enum, nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('external_subscription_id', sa.String(length=120), nullable=True),
        sa.Column(
            'id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False
        ),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text("timezone('utc', now())"),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text("timezone('utc', now())"),
            nullable=False,
        ),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.ForeignKeyConstraint(['subscription_plan_id'], ['subscription_plan.id']),
        sa.ForeignKeyConstraint(['company_id'], ['company.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_user_subscription_user_id'),
        'user_subscription',
        ['user_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_user_subscription_subscription_plan_id'),
        'user_subscription',
        ['subscription_plan_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_user_subscription_company_id'),
        'user_subscription',
        ['company_id'],
        unique=False,
    )
    op.create_index(
        'uq_user_subscription_one_active_per_plan',
        'user_subscription',
        ['user_id', 'subscription_plan_id'],
        unique=True,
        postgresql_where=sa.text("status = 'ACTIVE' AND is_deleted IS FALSE"),
    )


def downgrade() -> None:
    op.drop_index(
        'uq_user_subscription_one_active_per_plan', table_name='user_subscription'
    )
    op.drop_index(
        op.f('ix_user_subscription_company_id'), table_name='user_subscription'
    )
    op.drop_index(
        op.f('ix_user_subscription_subscription_plan_id'),
        table_name='user_subscription',
    )
    op.drop_index(op.f('ix_user_subscription_user_id'), table_name='user_subscription')
    op.drop_table('user_subscription')
    user_subscription_status_enum.drop(op.get_bind(), checkfirst=True)
