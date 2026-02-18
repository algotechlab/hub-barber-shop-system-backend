from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import BaseModel


class ScheduleBlock(BaseModel):
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    employee_id: Mapped[UUID] = mapped_column(ForeignKey('employee.id'), nullable=False)
    is_block: Mapped[bool] = mapped_column(Boolean, default=False)
    company_id: Mapped[UUID] = mapped_column(ForeignKey('company.id'), nullable=False)
