from uuid import UUID

from pydantic import BaseModel, EmailStr


class OwnerLoginSchema(BaseModel):
    email: EmailStr
    password: str


class TokenOutSchema(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class EmployeeLoginSchema(BaseModel):
    phone: str
    password: str


class UserLoginSchema(BaseModel):
    phone: str


class TokenWithCompanyOutSchema(BaseModel):
    id: UUID
    name: str
    access_token: str
    token_type: str = 'bearer'
    company_id: UUID
