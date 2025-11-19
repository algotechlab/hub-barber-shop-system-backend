from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model.base import BaseModels


class Transaction(BaseModels):

    __tablename__ = "transactions"

    type: Mapped[str] = mapped_column(nullable=False)  # extra or payment
    amount: Mapped[float] = mapped_column(nullable=False, default=0.00)
    description: Mapped[str] = mapped_column(nullable=True)
    schedule_id: Mapped[int] = mapped_column(
        ForeignKey("schedule.id"), nullable=True
    )
    cash_register_id: Mapped[int] = mapped_column(
        ForeignKey("cash_registers.id"), nullable=False
    )
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"), nullable=False
    )
    created_by: Mapped[int] = mapped_column(
        ForeignKey("employees.id"), nullable=False
    )
    cash_register = relationship("CashRegister", back_populates="transactions")
    schedule = relationship("Schedule")
    company = relationship("Company")
    created_user = relationship("User")
