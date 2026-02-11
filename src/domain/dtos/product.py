from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ProductDTO(BaseModel):
    id: UUID
    name: str
    description: str
    price: Decimal
    category: str
    status: bool
    url_image: str
    company_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {'from_attributes': True}


class CreateProductDTO(BaseModel):
    name: str
    description: str
    price: Decimal
    category: str
    status: bool
    url_image: str
    company_id: UUID


class UpdateProductDTO(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    category: Optional[str] = None
    status: Optional[bool] = None
    url_image: Optional[str] = None
