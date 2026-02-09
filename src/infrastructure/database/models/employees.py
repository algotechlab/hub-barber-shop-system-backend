import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import BaseModel
from src.infrastructure.database.models.commom.employee_status import EmployeeRole


class Employee(BaseModel):
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    role: Mapped[str] = mapped_column(
        String(255), nullable=False, default=EmployeeRole.role_employee.value
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('company.id'), nullable=False
    )
