from decimal import Decimal as DecimalType
from typing import Optional
from uuid import UUID

from sqlalchemy import DECIMAL, Boolean, CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import BaseModel


class SubscriptionPlan(BaseModel):
    """
    Plano de assinatura ofertado pela empresa: preço mensal, serviço coberto
    e franquia de usos no mês (ou ilimitado se uses_per_month for NULL).
    O vínculo do cliente ao plano fica em `UserSubscription` (user + subscription_plan).
    """

    company_id: Mapped[UUID] = mapped_column(
        ForeignKey('company.id'), nullable=False, index=True
    )
    service_id: Mapped[UUID] = mapped_column(
        ForeignKey('service.id'), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[DecimalType] = mapped_column(DECIMAL(10, 2), nullable=False)
    uses_per_month: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc='NULL = ilimitado no mês; inteiro >= 1 = máximo de usos por mês civil.',
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        CheckConstraint(
            'uses_per_month IS NULL OR uses_per_month >= 1',
            name='ck_subscription_plan_uses_per_month_null_or_gte_1',
        ),
        CheckConstraint('price >= 0', name='ck_subscription_plan_price_gte_0'),
    )
