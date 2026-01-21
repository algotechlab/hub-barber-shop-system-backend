from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class UserSchema(BaseModel):
    id: UUID
    name: str
    email: str
    password: str
    is_active: bool
    company_id: UUID


class CreateUserSchema(BaseModel):
    name: str
    email: str
    password: str
    company_id: UUID


class UpdateUserSchema(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserOutSchema(BaseModel):
    id: UUID
    name: str
    email: str
    password: str
    is_active: bool
    company_id: UUID
