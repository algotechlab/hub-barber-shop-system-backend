from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class OwnerBaseDTO(BaseModel):
    id: UUID
    name: str
    email: str
    password: str
    phone: str

    model_config = {'from_attributes': True}


class OwnerOutDTO(BaseModel):
    id: UUID
    name: str
    email: str
    phone: str
    created_at: datetime

    model_config = {'from_attributes': True}


class CreateOwnerDTO(BaseModel):
    name: str
    email: str
    password: str
    phone: str


class UpdateOwnerDTO(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    phone: Optional[str] = None
