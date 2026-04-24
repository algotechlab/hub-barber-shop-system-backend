from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SubscriptionPlanProductLineOutDTO(BaseModel):
    product_id: UUID
    quantity: int


class SubscriptionPlanOutDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    name: str
    description: Optional[str] = None
    service_ids: List[UUID]
    product_lines: List[SubscriptionPlanProductLineOutDTO] = Field(default_factory=list)
    price: Decimal
    uses_per_month: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    is_deleted: bool


class SubscriptionPlanCreateDTO(BaseModel):
    company_id: UUID
    name: str
    description: Optional[str] = None
    service_ids: List[UUID] = Field(
        ...,
        min_length=1,
        description='Pelo menos um serviço do catálogo da empresa.',
    )
    product_lines: List[SubscriptionPlanProductLineOutDTO] = Field(default_factory=list)
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

    @field_validator('product_lines')
    @classmethod
    def _validate_product_qty(
        cls, v: List[SubscriptionPlanProductLineOutDTO]
    ) -> List[SubscriptionPlanProductLineOutDTO]:
        for line in v:
            if line.quantity < 1:
                raise ValueError('quantity do produto deve ser >= 1')
        return v

    @field_validator('service_ids')
    @classmethod
    def _validate_unique_service_ids(cls, v: List[UUID]) -> List[UUID]:
        if len(v) != len(set(v)):
            raise ValueError('service_ids não pode repetir o mesmo serviço')
        return v

    @model_validator(mode='after')
    def _validate_unique_product_ids(self) -> 'SubscriptionPlanCreateDTO':
        pids = [line.product_id for line in self.product_lines]
        if len(pids) != len(set(pids)):
            raise ValueError('product_lines não pode repetir o mesmo product_id')
        return self


class SubscriptionPlanUpdateDTO(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    service_ids: Optional[List[UUID]] = None
    product_lines: Optional[List[SubscriptionPlanProductLineOutDTO]] = None
    price: Optional[Decimal] = None
    uses_per_month: Optional[int] = None
    is_active: Optional[bool] = None

    @field_validator('uses_per_month')
    @classmethod
    def _validate_uses_per_month_update(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 1:
            raise ValueError('uses_per_month deve ser >= 1 ou omitido (ilimitado)')
        return v

    @field_validator('service_ids')
    @classmethod
    def _service_ids_len_if_set(cls, v: Optional[List[UUID]]) -> Optional[List[UUID]]:
        if v is not None and len(v) < 1:
            raise ValueError(
                'Informe ao menos um service_id se atualizar a lista de serviços'
            )
        return v

    @field_validator('product_lines')
    @classmethod
    def _validate_product_qty(
        cls,
        v: Optional[List[SubscriptionPlanProductLineOutDTO]],
    ) -> Optional[List[SubscriptionPlanProductLineOutDTO]]:
        if v is None:
            return v
        for line in v:
            if line.quantity < 1:
                raise ValueError('quantity do produto deve ser >= 1')
        return v

    @field_validator('service_ids')
    @classmethod
    def _validate_unique_service_ids(
        cls, v: Optional[List[UUID]]
    ) -> Optional[List[UUID]]:
        if v is not None and len(v) != len(set(v)):
            raise ValueError('service_ids não pode repetir o mesmo serviço')
        return v

    @model_validator(mode='after')
    def _validate_unique_product_ids(self) -> 'SubscriptionPlanUpdateDTO':
        if self.product_lines is None:
            return self
        pids = [line.product_id for line in self.product_lines]
        if len(pids) != len(set(pids)):
            raise ValueError('product_lines não pode repetir o mesmo product_id')
        return self
