from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class UserBaseDTO(BaseModel):
    name: str
    email: str
    password: str
    company_id: UUID


class UpdateUserDTO(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserOutDTO(UserBaseDTO):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {'from_attributes': True}
