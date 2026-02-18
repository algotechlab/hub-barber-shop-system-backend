from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import BaseModel


class Owner(BaseModel):
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
