"""add subscription_plan table

Revision ID: d1e2f3a4b5c7
Revises: c3f0a1b2c3d4
Create Date: 2026-04-23

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'd1e2f3a4b5c7'
down_revision: Union[str, Sequence[str], None] = 'c3f0a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'subscription_plan',
        sa.Column('company_id', sa.Uuid(), nullable=False),
        sa.Column('service_id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('price', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('uses_per_month', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
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
        sa.CheckConstraint('price >= 0', name='ck_subscription_plan_price_gte_0'),
        sa.CheckConstraint(
            'uses_per_month IS NULL OR uses_per_month >= 1',
            name='ck_subscription_plan_uses_per_month_null_or_gte_1',
        ),
        sa.ForeignKeyConstraint(['company_id'], ['company.id']),
        sa.ForeignKeyConstraint(['service_id'], ['service.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_subscription_plan_company_id'),
        'subscription_plan',
        ['company_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_subscription_plan_service_id'),
        'subscription_plan',
        ['service_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f('ix_subscription_plan_service_id'), table_name='subscription_plan'
    )
    op.drop_index(
        op.f('ix_subscription_plan_company_id'), table_name='subscription_plan'
    )
    op.drop_table('subscription_plan')
