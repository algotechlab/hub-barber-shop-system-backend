from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import DECIMAL, DateTime, ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import BaseModelWithEmployee
from src.infrastructure.database.models.commom.payment_method import PaymentMethod
from src.infrastructure.database.models.commom.payment_status import PaymentStatus


def _enum_values(enum_cls: type) -> list[str]:
    return [member.value for member in enum_cls]


class ScheduleFinance(BaseModelWithEmployee):
    schedule_id: Mapped[UUID] = mapped_column(
        ForeignKey('schedule.id'), nullable=False, unique=True, index=True
    )
    # Snapshot dos serviços no fechamento (espelha `schedule.service_id`).
    # Sem FK em ARRAY; integridade é garantida ao copiar do agendamento.
    service_id: Mapped[List[UUID]] = mapped_column(
        ARRAY(PG_UUID(as_uuid=True)),
        nullable=False,
        index=True,
    )
    company_id: Mapped[UUID] = mapped_column(ForeignKey('company.id'), nullable=False)
    amount_service: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    amount_product: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(10, 2), nullable=True
    )
    amount_discount: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(10, 2), nullable=True
    )
    amount_total: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    payment_method: Mapped[PaymentMethod] = mapped_column(
        SQLEnum(
            PaymentMethod,
            name='payment_method_enum',
            values_callable=_enum_values,
        ),
        nullable=False,
    )
    payment_status: Mapped[PaymentStatus] = mapped_column(
        SQLEnum(
            PaymentStatus,
            name='payment_status_enum',
            values_callable=_enum_values,
        ),
        nullable=False,
    )
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
