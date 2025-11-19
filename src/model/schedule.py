from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model.base import BaseModels


class Schedule(BaseModels):
    __tablename__ = "schedule"

    time_register: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.id"), nullable=False
    )
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    is_check: Mapped[bool] = mapped_column(Boolean, default=False)
    signature_id: Mapped[int] = mapped_column(
        ForeignKey("signatures.id"), nullable=True
    )
    extras = relationship("ScheduleExtra", back_populates="schedule")
    signature = relationship("Signature")
