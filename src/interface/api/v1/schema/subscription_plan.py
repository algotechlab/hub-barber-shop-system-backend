from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class SubscriptionPlanOutSchema(BaseModel):
    id: UUID
    company_id: UUID
    service_id: UUID
    name: str
    price: Decimal
    uses_per_month: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    is_deleted: bool


class CreateSubscriptionPlanSchema(BaseModel):
    service_id: UUID
    name: str = Field(min_length=1, max_length=100)
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
    service_id: Optional[UUID] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[Decimal] = Field(None, ge=0)
    uses_per_month: Optional[int] = None
    is_active: Optional[bool] = None

    @field_validator('uses_per_month')
    @classmethod
    def _validate_uses_per_month_update(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 1:
            raise ValueError('uses_per_month deve ser >= 1')
        return v
