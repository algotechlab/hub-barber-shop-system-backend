from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserSubscriptionOutDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    subscription_plan_id: UUID
    company_id: UUID
    status: Literal['ACTIVE', 'CANCELED', 'EXPIRED']
    started_at: datetime
    ended_at: Optional[datetime] = None
    external_subscription_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool


class UserSubscriptionWithPlanOutDTO(UserSubscriptionOutDTO):
    """Assinatura do usuário com dados do plano (para exibição no app)."""

    plan_name: str
    plan_price: Decimal
    service_id: UUID
    plan_uses_per_month: Optional[int] = Field(
        default=None,
        description='Franquia mensal do plano; None = ilimitado.',
    )


class UserSubscriptionCreateDTO(BaseModel):
    user_id: UUID
    company_id: UUID
    subscription_plan_id: UUID
    started_at: Optional[datetime] = None
    external_subscription_id: Optional[str] = None
