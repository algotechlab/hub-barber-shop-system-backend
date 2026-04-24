from datetime import datetime
from decimal import Decimal
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.interface.api.v1.schema.subscription_plan import (
    SubscriptionPlanProductLineSchema,
)


class CreateUserSubscriptionSchema(BaseModel):
    subscription_plan_id: UUID = Field(
        description='ID do plano (catálogo) ao qual o usuário está se associando',
    )
    external_subscription_id: Optional[str] = Field(
        default=None,
        max_length=120,
        description=(
            'Opcional: id no provedor de pagamento, se já existir no momento do pedido'
        ),
    )


class ActivateUserSubscriptionAfterPaymentSchema(BaseModel):
    payment_method: Literal['CREDIT_CARD', 'DEBIT_CARD', 'PIX', 'MONEY', 'OTHER'] = (
        Field(
            description='Como o cliente pagou (PIX, cartões ou dinheiro).',
        )
    )
    payment_at: Optional[datetime] = Field(
        default=None,
        description=(
            'Momento do pagamento; se omitido, usa a data/hora do servidor (UTC) '
            'na confirmação.'
        ),
    )
    external_subscription_id: Optional[str] = Field(
        default=None,
        max_length=120,
        description=(
            'Opcional: atualiza o id externo na ativação (ex. após confirmação no PDV)'
        ),
    )


class UserSubscriptionOutSchema(BaseModel):
    id: UUID
    user_id: UUID
    subscription_plan_id: UUID
    company_id: UUID
    status: Literal['PENDING_PAYMENT', 'ACTIVE', 'CANCELED', 'EXPIRED']
    started_at: datetime
    ended_at: Optional[datetime] = None
    external_subscription_id: Optional[str] = None
    payment_at: Optional[datetime] = None
    payment_method: Optional[
        Literal['CREDIT_CARD', 'DEBIT_CARD', 'PIX', 'MONEY', 'OTHER']
    ] = None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool


class UserSubscriptionWithPlanOutSchema(UserSubscriptionOutSchema):
    plan_name: str
    plan_price: Decimal
    plan_description: Optional[str] = None
    service_ids: List[UUID] = Field(default_factory=list)
    plan_product_lines: List[SubscriptionPlanProductLineSchema] = Field(
        default_factory=list
    )
    plan_uses_per_month: Optional[int] = Field(
        default=None,
        description='Franquia mensal do plano; null = ilimitado.',
    )


class UserSubscriptionWithPlanAndClientOutSchema(UserSubscriptionWithPlanOutSchema):
    client_name: str = Field(
        description='Nome do cliente (mesmo do cadastro de usuário).',
    )
