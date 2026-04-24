from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class SubscriptionPlanProductLineSchema(BaseModel):
    product_id: UUID
    quantity: int = Field(default=1, ge=1)


class SubscriptionPlanOutSchema(BaseModel):
    id: UUID
    company_id: UUID
    name: str
    description: Optional[str] = None
    service_ids: List[UUID] = Field(default_factory=list)
    product_lines: List[SubscriptionPlanProductLineSchema] = Field(default_factory=list)
    price: Decimal
    uses_per_month: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    @field_validator('product_lines', 'service_ids', mode='before')
    @classmethod
    def _default_lists(cls, v):
        return v or []


class CreateSubscriptionPlanSchema(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    service_ids: List[UUID] = Field(
        min_length=1, description='Pelo menos um serviço do catálogo da empresa'
    )
    product_lines: List[SubscriptionPlanProductLineSchema] = Field(default_factory=list)
    price: Decimal = Field(..., ge=0)
    uses_per_month: Optional[int] = Field(
        default=None,
        description='Omitir ou null = ilimitado; caso informado, mínimo 1.',
    )
    is_active: bool = True

    @field_validator('uses_per_month')
    @classmethod
    def _validate_uses_per_month(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 1:
            raise ValueError('uses_per_month deve ser >= 1')
        return v


class UpdateSubscriptionPlanSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    service_ids: Optional[List[UUID]] = None
    product_lines: Optional[List[SubscriptionPlanProductLineSchema]] = None
    price: Optional[Decimal] = Field(None, ge=0)
    uses_per_month: Optional[int] = None
    is_active: Optional[bool] = None

    @field_validator('uses_per_month')
    @classmethod
    def _validate_uses_per_month_update(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 1:
            raise ValueError('uses_per_month deve ser >= 1')
        return v
