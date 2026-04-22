"""add cash register sessions and adjustments

Revision ID: c3f0a1b2c3d4
Revises: a1b2c3d4e5f6
Create Date: 2026-04-22 14:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = 'c3f0a1b2c3d4'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# create_type=False: o tipo é criado explicitamente em upgrade() com checkfirst=True;
# a coluna só referencia o ENUM existente (evita CREATE TYPE duplicado no create_table).
cash_movement_kind_enum = postgresql.ENUM(
    'SUPPLY',
    'WITHDRAWAL',
    name='cash_movement_kind_enum',
    create_type=False,
)


def upgrade() -> None:
    cash_movement_kind_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'cash_register_session',
        sa.Column('company_id', sa.Uuid(), nullable=False),
        sa.Column('opened_by', sa.Uuid(), nullable=False),
        sa.Column('closed_by', sa.Uuid(), nullable=True),
        sa.Column(
            'opened_at',
            sa.DateTime(timezone=True),
            server_default=sa.text("timezone('utc', now())"),
            nullable=False,
        ),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('opening_balance', sa.DECIMAL(precision=12, scale=2), nullable=False),
        sa.Column('closing_balance', sa.DECIMAL(precision=12, scale=2), nullable=True),
        sa.Column('expected_balance', sa.DECIMAL(precision=12, scale=2), nullable=True),
        sa.Column('opening_notes', sa.String(length=500), nullable=True),
        sa.Column('closing_notes', sa.Text(), nullable=True),
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
        sa.CheckConstraint(
            'opening_balance >= 0', name='ck_cash_register_session_opening_gte_0'
        ),
        sa.CheckConstraint(
            '(closing_balance IS NULL OR closing_balance >= 0)',
            name='ck_cash_register_session_closing_gte_0',
        ),
        sa.ForeignKeyConstraint(['company_id'], ['company.id']),
        sa.ForeignKeyConstraint(['opened_by'], ['employee.id']),
        sa.ForeignKeyConstraint(['closed_by'], ['employee.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_cash_register_session_company_id'),
        'cash_register_session',
        ['company_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_cash_register_session_opened_by'),
        'cash_register_session',
        ['opened_by'],
        unique=False,
    )
    op.create_index(
        op.f('ix_cash_register_session_closed_by'),
        'cash_register_session',
        ['closed_by'],
        unique=False,
    )
    op.create_index(
        op.f('ix_cash_register_session_closed_at'),
        'cash_register_session',
        ['closed_at'],
        unique=False,
    )
    op.create_index(
        'uq_cash_register_session_company_open',
        'cash_register_session',
        ['company_id'],
        unique=True,
        postgresql_where=sa.text('closed_at IS NULL AND is_deleted IS FALSE'),
    )

    op.create_table(
        'cash_register_adjustment',
        sa.Column('session_id', sa.Uuid(), nullable=False),
        sa.Column('company_id', sa.Uuid(), nullable=False),
        sa.Column('kind', cash_movement_kind_enum, nullable=False),
        sa.Column('amount', sa.DECIMAL(precision=12, scale=2), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=False),
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
        sa.CheckConstraint(
            'amount > 0', name='ck_cash_register_adjustment_amount_gt_0'
        ),
        sa.ForeignKeyConstraint(
            ['session_id'],
            ['cash_register_session.id'],
        ),
        sa.ForeignKeyConstraint(['company_id'], ['company.id']),
        sa.ForeignKeyConstraint(['created_by'], ['employee.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_cash_register_adjustment_session_id'),
        'cash_register_adjustment',
        ['session_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_cash_register_adjustment_company_id'),
        'cash_register_adjustment',
        ['company_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_cash_register_adjustment_created_by'),
        'cash_register_adjustment',
        ['created_by'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f('ix_cash_register_adjustment_created_by'),
        table_name='cash_register_adjustment',
    )
    op.drop_index(
        op.f('ix_cash_register_adjustment_company_id'),
        table_name='cash_register_adjustment',
    )
    op.drop_index(
        op.f('ix_cash_register_adjustment_session_id'),
        table_name='cash_register_adjustment',
    )
    op.drop_table('cash_register_adjustment')

    op.drop_index(
        'uq_cash_register_session_company_open', table_name='cash_register_session'
    )
    op.drop_index(
        op.f('ix_cash_register_session_closed_at'), table_name='cash_register_session'
    )
    op.drop_index(
        op.f('ix_cash_register_session_closed_by'), table_name='cash_register_session'
    )
    op.drop_index(
        op.f('ix_cash_register_session_opened_by'), table_name='cash_register_session'
    )
    op.drop_index(
        op.f('ix_cash_register_session_company_id'), table_name='cash_register_session'
    )
    op.drop_table('cash_register_session')

    cash_movement_kind_enum.drop(op.get_bind(), checkfirst=True)
