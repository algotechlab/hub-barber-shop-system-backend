from decimal import Decimal

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model.base import BaseModels


class CashRegister(BaseModels):

    __tablename__ = "cash_registers"

    opening_balance: Mapped[float] = mapped_column(
        nullable=False, default=Decimal("0.00")
    )
    closing_balance: Mapped[float] = mapped_column(nullable=True)
    date: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False, default="open")  #
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"), nullable=False
    )
    opened_by: Mapped[int] = mapped_column(
        ForeignKey("employees.id"), nullable=False
    )
    closed_by: Mapped[int] = mapped_column(
        ForeignKey("employees.id"), nullable=True
    )

    # Relacionamentos
    company = relationship("Company", back_populates="cash_registers")
    transactions = relationship(
        "Transaction",
        back_populates="cash_register",
        cascade="all, delete-orphan",
    )
    opened_user = relationship("User", foreign_keys=[opened_by])
    closed_user = relationship("User", foreign_keys=[closed_by])
