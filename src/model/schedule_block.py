from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import BaseModels


class ScheduleBlock(BaseModels):
    __tablename__ = "block"

    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id"), nullable=False
    )

    is_block: Mapped[bool] = mapped_column(Boolean, default=False)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"), nullable=False
    )
