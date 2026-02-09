from decimal import Decimal as DecimalType
from uuid import UUID

from sqlalchemy import DECIMAL, Boolean, ForeignKey, Integer, Interval, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import BaseModel


class Service(BaseModel):
    name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(30), nullable=False)
    price: Mapped[DecimalType] = mapped_column(DECIMAL, nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    time_to_spend: Mapped[Interval] = mapped_column(Interval, nullable=False)
    status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    company_id: Mapped[UUID] = mapped_column(ForeignKey('company.id'), nullable=False)
