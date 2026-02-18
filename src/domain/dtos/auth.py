from uuid import UUID

from pydantic import BaseModel, EmailStr


class OwnerLoginDTO(BaseModel):
    email: EmailStr
    password: str


class OwnerAuthDTO(BaseModel):
    id: UUID
    password: str

    model_config = {'from_attributes': True}


class EmployeeLoginDTO(BaseModel):
    phone: str
    password: str


class UserLoginDTO(BaseModel):
    phone: str


class EmployeeAuthDTO(BaseModel):
    id: UUID
    name: str
    password: str
    company_id: UUID

    model_config = {'from_attributes': True}


class UserAuthDTO(BaseModel):
    id: UUID
    name: str
    company_id: UUID

    model_config = {'from_attributes': True}


class TokenDTO(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class TokenWithCompanyDTO(BaseModel):
    id: UUID
    name: str
    access_token: str
    token_type: str = 'bearer'
    company_id: UUID
