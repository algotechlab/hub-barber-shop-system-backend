from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CompanyDTO(BaseModel):
    id: UUID
    name: str
    slug: str
    is_active: bool
    owner_id: UUID

    model_config = {'from_attributes': True}


class CreateCompanyDTO(BaseModel):
    name: str
    slug: str
    is_active: bool
    owner_id: UUID


class CompanyOutDTO(BaseModel):
    id: UUID
    name: str
    slug: str
    is_active: bool
    owner_id: UUID
    created_at: datetime

    model_config = {'from_attributes': True}
