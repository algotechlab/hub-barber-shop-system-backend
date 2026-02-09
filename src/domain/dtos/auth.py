from uuid import UUID

from pydantic import BaseModel, EmailStr


class OwnerLoginDTO(BaseModel):
    email: EmailStr
    password: str


class OwnerAuthDTO(BaseModel):
    id: UUID
    password: str

    model_config = {'from_attributes': True}


class TokenDTO(BaseModel):
    access_token: str
    token_type: str = 'bearer'
