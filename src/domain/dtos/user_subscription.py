from datetime import datetime
from decimal import Decimal
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.domain.dtos.subscription_plan import SubscriptionPlanProductLineOutDTO

PaymentMethodLiteral = Literal['CREDIT_CARD', 'DEBIT_CARD', 'PIX', 'MONEY', 'OTHER']


class UserSubscriptionOutDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    subscription_plan_id: UUID
    company_id: UUID
    status: Literal['PENDING_PAYMENT', 'ACTIVE', 'CANCELED', 'EXPIRED']
    started_at: datetime
    ended_at: Optional[datetime] = None
    external_subscription_id: Optional[str] = None
    payment_at: Optional[datetime] = None
    payment_method: Optional[PaymentMethodLiteral] = None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool


class UserSubscriptionWithPlanOutDTO(UserSubscriptionOutDTO):
    """Assinatura do usuário com dados do plano (para exibição no app)."""

    plan_name: str
    plan_price: Decimal
    plan_description: Optional[str] = None
    service_ids: List[UUID] = Field(default_factory=list)
    plan_product_lines: List[SubscriptionPlanProductLineOutDTO] = Field(
        default_factory=list
    )
    plan_uses_per_month: Optional[int] = Field(
        default=None,
        description='Franquia mensal do plano; None = ilimitado.',
    )


class UserSubscriptionWithPlanAndClientOutDTO(UserSubscriptionWithPlanOutDTO):
    """Listagem de pendentes no painel: plano + nome do cliente."""

    client_name: str


class UserSubscriptionCreateDTO(BaseModel):
    user_id: UUID
    company_id: UUID
    subscription_plan_id: UUID
    status: Literal['PENDING_PAYMENT', 'ACTIVE'] = 'PENDING_PAYMENT'
    started_at: Optional[datetime] = None
    external_subscription_id: Optional[str] = None
