from decimal import Decimal

from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from src.model.base import BaseModels


class CashRegister(BaseModels):

    __tablename__ = "cash_registers"

    opening_balance = Column(Numeric(10, 2), default=Decimal("0.00"))
    closing_balance = Column(Numeric(10, 2))
    date = Column(Date)
    status = Column(String(20), default="open")  # open, closed
    company_id = Column(Integer, ForeignKey("companies.id"))
    opened_by = Column(Integer, ForeignKey("users.id"))
    closed_by = Column(Integer, ForeignKey("users.id"))
    # Relacionamentos
    company = relationship("Company", back_populates="cash_registers")
    transactions = relationship(
        "Transaction",
        back_populates="cash_register",
        cascade="all, delete-orphan",
    )
    opened_user = relationship("User", foreign_keys=[opened_by])
    closed_user = relationship("User", foreign_keys=[closed_by])
