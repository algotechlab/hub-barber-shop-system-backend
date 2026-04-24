"""subscription plan multiline (description, services, products)

Revision ID: b2c3d4e5f6a0
Revises: a1b2c3d4e5f7
Create Date: 2026-04-25

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'b2c3d4e5f6a0'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'subscription_plan',
        sa.Column('description', sa.Text(), nullable=True),
    )
    op.create_table(
        'subscription_plan_service',
        sa.Column(
            'subscription_plan_id',
            sa.Uuid(),
            sa.ForeignKey('subscription_plan.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column('service_id', sa.Uuid(), sa.ForeignKey('service.id'), nullable=False),
        sa.PrimaryKeyConstraint('subscription_plan_id', 'service_id'),
    )
    op.create_index(
        'ix_sub_plan_service_plan',
        'subscription_plan_service',
        ['subscription_plan_id'],
    )
    op.create_index(
        'ix_sub_plan_service_svc', 'subscription_plan_service', ['service_id']
    )

    op.create_table(
        'subscription_plan_product',
        sa.Column(
            'subscription_plan_id',
            sa.Uuid(),
            sa.ForeignKey('subscription_plan.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column('product_id', sa.Uuid(), sa.ForeignKey('product.id'), nullable=False),
        sa.Column('quantity', sa.Integer(), server_default='1', nullable=False),
        sa.CheckConstraint(
            'quantity >= 1', name='ck_subscription_plan_product_qty_gte_1'
        ),
        sa.PrimaryKeyConstraint('subscription_plan_id', 'product_id'),
    )
    op.create_index(
        'ix_sub_plan_product_plan',
        'subscription_plan_product',
        ['subscription_plan_id'],
    )
    op.create_index(
        'ix_sub_plan_product_product',
        'subscription_plan_product',
        ['product_id'],
    )

    op.execute(
        sa.text(
            'INSERT INTO subscription_plan_service (subscription_plan_id, service_id) '
            'SELECT id, service_id FROM subscription_plan'
        )
    )

    op.drop_index('ix_subscription_plan_service_id', table_name='subscription_plan')
    op.drop_constraint(
        'subscription_plan_service_id_fkey', 'subscription_plan', type_='foreignkey'
    )
    op.drop_column('subscription_plan', 'service_id')


def downgrade() -> None:  # noqa: N802
    op.add_column(
        'subscription_plan',
        sa.Column('service_id', sa.Uuid(), nullable=True),
    )
    # restore from first line (best effort)
    op.execute(
        sa.text(
            'UPDATE subscription_plan p SET service_id = s.service_id FROM ('
            '  SELECT DISTINCT ON (subscription_plan_id) '
            '  subscription_plan_id, service_id '
            '  FROM subscription_plan_service'
            ') s WHERE p.id = s.subscription_plan_id'
        )
    )
    op.alter_column('subscription_plan', 'service_id', nullable=False)
    op.create_foreign_key(
        'subscription_plan_service_id_fkey',
        'subscription_plan',
        'service',
        ['service_id'],
        ['id'],
    )
    op.create_index(
        'ix_subscription_plan_service_id', 'subscription_plan', ['service_id']
    )

    op.drop_index('ix_sub_plan_product_product', table_name='subscription_plan_product')
    op.drop_index('ix_sub_plan_product_plan', table_name='subscription_plan_product')
    op.drop_table('subscription_plan_product')

    op.drop_index('ix_sub_plan_service_svc', table_name='subscription_plan_service')
    op.drop_index('ix_sub_plan_service_plan', table_name='subscription_plan_service')
    op.drop_table('subscription_plan_service')
    op.drop_column('subscription_plan', 'description')
