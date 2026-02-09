from uuid import UUID

from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import BaseModel


class EmployeeCompanies(BaseModel):
    employee_id: Mapped[UUID] = mapped_column(ForeignKey('employee.id'), nullable=False)
    company_id: Mapped[UUID] = mapped_column(ForeignKey('company.id'), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
