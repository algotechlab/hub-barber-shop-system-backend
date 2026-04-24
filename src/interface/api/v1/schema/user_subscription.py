from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CreateUserSubscriptionSchema(BaseModel):
    subscription_plan_id: UUID = Field(
        description='ID do plano (catálogo) ao qual o usuário está se associando',
    )
    external_subscription_id: Optional[str] = Field(
        default=None,
        max_length=120,
        description='Opcional: id retornado pelo provedor de pagamento',
    )


class UserSubscriptionOutSchema(BaseModel):
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


class UserSubscriptionWithPlanOutSchema(UserSubscriptionOutSchema):
    plan_name: str
    plan_price: Decimal
    service_id: UUID
    plan_uses_per_month: Optional[int] = Field(
        default=None,
        description='Franquia mensal do plano; null = ilimitado.',
    )
