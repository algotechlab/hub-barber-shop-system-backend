from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DECIMAL

from src.infrastructure.database.models.base import BaseModel, BaseModelWithEmployee
from src.infrastructure.database.models.commom.cash_movement_kind import (
    CashMovementKind,
)


def _enum_values(enum_cls: type) -> list[str]:
    return [member.value for member in enum_cls]


class CashRegisterSession(BaseModel):
    """
    Turno de caixa: abertura (saldo inicial) e fechamento (conferência).
    Entradas por vendas vêm de `schedule_finance` (fechamento de agendamento),
    contabilizadas pelo `created_at` do registro e por status,
    (exceto cancelado/reembolso);
    saídas operacionais de `expense`; ajustes em `cash_register_adjustment`.
    """

    company_id: Mapped[UUID] = mapped_column(
        ForeignKey('company.id'), nullable=False, index=True
    )
    opened_by: Mapped[UUID] = mapped_column(
        ForeignKey('employee.id'), nullable=False, index=True
    )
    closed_by: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey('employee.id'), nullable=True, index=True
    )
    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    closed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    opening_balance: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False)
    closing_balance: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(12, 2), nullable=True
    )
    expected_balance: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(12, 2), nullable=True
    )
    opening_notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    closing_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class CashRegisterAdjustment(BaseModelWithEmployee):
    """Lançamento manual no caixa aberto (suprimento ou sangria)."""

    session_id: Mapped[UUID] = mapped_column(
        ForeignKey('cash_register_session.id'), nullable=False, index=True
    )
    company_id: Mapped[UUID] = mapped_column(
        ForeignKey('company.id'), nullable=False, index=True
    )
    kind: Mapped[CashMovementKind] = mapped_column(
        SQLEnum(
            CashMovementKind,
            name='cash_movement_kind_enum',
            values_callable=_enum_values,
        ),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
