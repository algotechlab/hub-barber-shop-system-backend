from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProductSchema(BaseModel):
    id: UUID
    name: str
    description: str
    price: Decimal
    category: str
    status: bool
    url_image: str
    company_id: UUID


class ProductOutSchema(ProductSchema):
    created_at: datetime
    updated_at: datetime


class CreateProductSchema(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    description: str = Field(min_length=3, max_length=30)
    price: Decimal = Field(..., gt=0, description='Preço do produto')
    category: str = Field(min_length=3, max_length=30)
    status: bool = Field(default=True)
    url_image: str = Field(min_length=3, max_length=255)


class UpdateProductSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = Field(None, min_length=3, max_length=30)
    price: Optional[Decimal] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=3, max_length=30)
    status: Optional[bool] = None
    url_image: Optional[str] = Field(None, min_length=3, max_length=255)


class UploadProductImageOutSchema(BaseModel):
    url: str
