from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import BaseModel
from src.infrastructure.database.models.commom.user_subscription_status import (
    UserSubscriptionStatus,
)


def _enum_values(enum_cls: type) -> list[str]:
    return [member.value for member in enum_cls]


class UserSubscription(BaseModel):
    """
    Vínculo do usuário a um plano (quem consome a assinatura).
    O catálogo do plano permanece em `SubscriptionPlan`.
    """

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('user.id'), nullable=False, index=True
    )
    subscription_plan_id: Mapped[UUID] = mapped_column(
        ForeignKey('subscription_plan.id'), nullable=False, index=True
    )
    company_id: Mapped[UUID] = mapped_column(
        ForeignKey('company.id'), nullable=False, index=True
    )
    status: Mapped[UserSubscriptionStatus] = mapped_column(
        SQLEnum(
            UserSubscriptionStatus,
            name='user_subscription_status_enum',
            values_callable=_enum_values,
        ),
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    external_subscription_id: Mapped[Optional[str]] = mapped_column(
        String(120),
        nullable=True,
        doc='Ex.: id de preapproval / assinatura no provedor de pagamento.',
    )
