from sqlalchemy import Float, ForeignKey, Interval, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import BaseModels


class Product(BaseModels):
    __tablename__ = "product"
    description: Mapped[str] = mapped_column(String(30), nullable=False)
    value_operation: Mapped[Numeric] = mapped_column(
        Numeric(10, 2), default=0.00, nullable=False
    )
    time_to_spend: Mapped[Interval] = mapped_column(Interval, nullable=False)
    commission: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"), nullable=False
    )
