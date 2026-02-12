from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class CreateServiceSchema(BaseModel):
    name: str
    description: str
    price: float
    duration: int
    category: str
    time_to_spend: int
    status: bool
    url_image: str


class ServiceSchema(BaseModel):
    id: UUID
    name: str
    description: str
    price: float
    duration: int
    category: str
    time_to_spend: int
    status: bool
    url_image: str


class UpdateServiceSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    duration: Optional[int] = None
    category: Optional[str] = None
    time_to_spend: Optional[int] = None
    status: Optional[bool] = None
    url_image: Optional[str] = None


class UploadServiceImageOutSchema(BaseModel):
    url: str
