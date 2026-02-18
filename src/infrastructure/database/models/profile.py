from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import BaseModel


class Profile(BaseModel):
    color: Mapped[str] = mapped_column(String(20), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    employee_id: Mapped[UUID] = mapped_column(ForeignKey('employee.id'), nullable=False)
    company_id: Mapped[UUID] = mapped_column(ForeignKey('company.id'), nullable=False)
