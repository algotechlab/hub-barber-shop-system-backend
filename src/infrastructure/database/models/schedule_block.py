from datetime import date, time
from uuid import UUID

from sqlalchemy import Boolean, Date, ForeignKey, Time
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import BaseModel


class ScheduleBlock(BaseModel):
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    employee_id: Mapped[UUID] = mapped_column(ForeignKey('employee.id'), nullable=False)
    is_block: Mapped[bool] = mapped_column(Boolean, default=False)
    company_id: Mapped[UUID] = mapped_column(ForeignKey('company.id'), nullable=False)
