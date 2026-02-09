from pydantic import BaseModel, EmailStr


class OwnerLoginSchema(BaseModel):
    email: EmailStr
    password: str


class TokenOutSchema(BaseModel):
    access_token: str
    token_type: str = 'bearer'
