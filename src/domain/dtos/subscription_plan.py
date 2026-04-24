from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SubscriptionPlanOutDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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


class SubscriptionPlanCreateDTO(BaseModel):
    company_id: UUID
    service_id: UUID
    name: str
    price: Decimal = Field(ge=0)
    uses_per_month: Optional[int] = Field(
        default=None,
        description='None = ilimitado; se informado, >= 1',
    )
    is_active: bool = True

    @field_validator('uses_per_month')
    @classmethod
    def _validate_uses_per_month(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 1:
            raise ValueError('uses_per_month deve ser >= 1 ou omitido (ilimitado)')
        return v


class SubscriptionPlanUpdateDTO(BaseModel):
    service_id: Optional[UUID] = None
    name: Optional[str] = None
    price: Optional[Decimal] = None
    uses_per_month: Optional[int] = None
    is_active: Optional[bool] = None

    @field_validator('uses_per_month')
    @classmethod
    def _validate_uses_per_month_update(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 1:
            raise ValueError('uses_per_month deve ser >= 1 ou omitido (ilimitado)')
        return v
