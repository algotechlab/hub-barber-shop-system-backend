"""add schedule finance and expense

Revision ID: 9a7a0f2b1c3d
Revises: 4fa983a118ed
Create Date: 2026-03-11 12:10:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9a7a0f2b1c3d'
down_revision: Union[str, Sequence[str], None] = '4fa983a118ed'
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
payment_status_enum = postgresql.ENUM(
    'PENDING',
    'PAID',
    'CANCELED',
    'REFUNDED',
    name='payment_status_enum',
    create_type=False,
)


def upgrade() -> None:
    """Upgrade schema."""
    payment_method_enum.create(op.get_bind(), checkfirst=True)
    payment_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'schedule_finance',
        sa.Column('schedule_id', sa.Uuid(), nullable=False),
        sa.Column('company_id', sa.Uuid(), nullable=False),
        sa.Column('amount_service', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('amount_product', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('amount_discount', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('amount_total', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('payment_method', payment_method_enum, nullable=False),
        sa.Column('payment_status', payment_status_enum, nullable=False),
        sa.Column('paid_at', sa.DateTime(), nullable=True),
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
            'amount_service >= 0', name='ck_schedule_finance_service_gte_0'
        ),
        sa.CheckConstraint('amount_total >= 0', name='ck_schedule_finance_total_gte_0'),
        sa.CheckConstraint(
            '(amount_discount IS NULL OR amount_discount >= 0)',
            name='ck_schedule_finance_discount_gte_0',
        ),
        sa.ForeignKeyConstraint(['company_id'], ['company.id']),
        sa.ForeignKeyConstraint(['created_by'], ['employee.id']),
        sa.ForeignKeyConstraint(['schedule_id'], ['schedule.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('schedule_id'),
    )
    op.create_index(
        op.f('ix_schedule_finance_schedule_id'),
        'schedule_finance',
        ['schedule_id'],
        unique=True,
    )
    op.create_index(
        op.f('ix_schedule_finance_created_by'),
        'schedule_finance',
        ['created_by'],
        unique=False,
    )

    op.create_table(
        'expense',
        sa.Column('company_id', sa.Uuid(), nullable=False),
        sa.Column('employee_id', sa.Uuid(), nullable=True),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('occurred_at', sa.DateTime(), nullable=False),
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
        sa.CheckConstraint('amount >= 0', name='ck_expense_amount_gte_0'),
        sa.ForeignKeyConstraint(['company_id'], ['company.id']),
        sa.ForeignKeyConstraint(['created_by'], ['employee.id']),
        sa.ForeignKeyConstraint(['employee_id'], ['employee.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_expense_company_id'), 'expense', ['company_id'], unique=False
    )
    op.create_index(
        op.f('ix_expense_created_by'), 'expense', ['created_by'], unique=False
    )
    op.create_index(
        op.f('ix_expense_employee_id'), 'expense', ['employee_id'], unique=False
    )
    op.create_index(
        op.f('ix_expense_occurred_at'), 'expense', ['occurred_at'], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_expense_occurred_at'), table_name='expense')
    op.drop_index(op.f('ix_expense_employee_id'), table_name='expense')
    op.drop_index(op.f('ix_expense_created_by'), table_name='expense')
    op.drop_index(op.f('ix_expense_company_id'), table_name='expense')
    op.drop_table('expense')

    op.drop_index(op.f('ix_schedule_finance_created_by'), table_name='schedule_finance')
    op.drop_index(
        op.f('ix_schedule_finance_schedule_id'), table_name='schedule_finance'
    )
    op.drop_table('schedule_finance')

    payment_status_enum.drop(op.get_bind(), checkfirst=True)
    payment_method_enum.drop(op.get_bind(), checkfirst=True)
