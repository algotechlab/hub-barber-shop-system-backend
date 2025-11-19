from decimal import Decimal

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import BaseModels


class Signature(BaseModels):

    __tablename__ = "signatures"
    name: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    valu: Mapped[float] = mapped_column(
        nullable=False, default=Decimal("0.00")
    )
    days_date: Mapped[int] = mapped_column(nullable=False)
    expiry_date: Mapped[str] = mapped_column(nullable=False)
    count_use: Mapped[int] = mapped_column(nullable=False, default=0)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
