from uuid import UUID

from pydantic import BaseModel


class CompanySchema(BaseModel):
    id: UUID
    name: str
    slug: str
    is_active: bool
    owner_id: UUID


class CreateCompanySchema(BaseModel):
    name: str
    slug: str
    is_active: bool


class CompanyOutSchema(BaseModel):
    id: UUID
    name: str
    slug: str
    is_active: bool
    owner_id: UUID
