from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator


class ServiceDTO(BaseModel):
    id: UUID
    name: str
    description: str
    price: Decimal
    duration: int
    category: str
    time_to_spend: int
    status: bool
    url_image: str
    company_id: UUID

    model_config = {'from_attributes': True}

    @field_validator('time_to_spend', mode='before')
    @classmethod
    def _normalize_time_to_spend(cls, value: object) -> object:
        if isinstance(value, timedelta):
            return int(value.total_seconds() // 60)
        return value


class CreateServiceDTO(BaseModel):
    name: str
    description: str
    price: Decimal
    duration: int
    category: str
    time_to_spend: int
    status: bool
    url_image: str
    company_id: UUID


class UpdateServiceDTO(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    duration: Optional[int] = None
    category: Optional[str] = None
    time_to_spend: Optional[int] = None
    status: Optional[bool] = None
    url_image: Optional[str] = None


class ServiceOutDTO(BaseModel):
    id: UUID
    name: str
    description: str
    price: Decimal
    duration: int
    category: str
    time_to_spend: int
    status: bool
    url_image: str
    created_at: datetime

    model_config = {'from_attributes': True}

    @field_validator('time_to_spend', mode='before')
    @classmethod
    def _normalize_time_to_spend(cls, value: object) -> object:
        if isinstance(value, timedelta):
            return int(value.total_seconds() // 60)
        return value
