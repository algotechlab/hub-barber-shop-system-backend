from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model.base import BaseModels


class ScheduleExtra(BaseModels):
    __tablename__ = "schedule_extras"

    schedule_id: Mapped[int] = mapped_column(
        ForeignKey("schedule.id"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(default=1)

    product = relationship("Product")
    schedule = relationship("Schedule", back_populates="extras")
