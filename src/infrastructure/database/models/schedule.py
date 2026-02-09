from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import BaseModel


class Schedule(BaseModel):
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('user.id'), nullable=False, index=True
    )
    service_id: Mapped[UUID] = mapped_column(
        ForeignKey('service.id'), nullable=False, index=True
    )
    product_id: Mapped[UUID] = mapped_column(
        ForeignKey('product.id'), nullable=False, index=True
    )
    employee_id: Mapped[UUID] = mapped_column(
        ForeignKey('employee.id'), nullable=False, index=True
    )
    company_id: Mapped[UUID] = mapped_column(
        ForeignKey('company.id'), nullable=False, index=True
    )
    time_register: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True
    )
    time_start: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    time_end: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_canceled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
