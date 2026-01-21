from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class EmployeeSchema(BaseModel):
    id: UUID
    name: str
    last_name: str
    phone: str
    password: str
    is_active: bool
    role: str
    company_id: UUID


class EmployeeOutSchema(BaseModel):
    id: UUID
    name: str
    last_name: str
    phone: str
    password: str
    is_active: bool
    role: str
    company_id: UUID
    created_at: datetime
    updated_at: datetime


class CreateEmployeeSchema(BaseModel):
    name: str
    last_name: str
    phone: str
    password: str
    is_active: bool
    role: str
    company_id: UUID


class UpdateEmployeeSchema(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None
    company_id: Optional[UUID] = None
