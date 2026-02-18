from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import BaseModel


class User(BaseModel):
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    company_id: Mapped[UUID] = mapped_column(ForeignKey('company.id'), nullable=False)
    recurring_plan: Mapped[str] = mapped_column(
        String(20), nullable=True, default='free_plan'
    )
