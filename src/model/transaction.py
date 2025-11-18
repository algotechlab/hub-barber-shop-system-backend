from sqlalchemy import Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from src.model.base import BaseModels


class Transaction(BaseModels):

    __tablename__ = "transactions"

    type = Column(String(10))  # 'entry' or 'exit'
    amount = Column(Numeric(10, 2))
    description = Column(String(100))
    schedule_id = Column(Integer, ForeignKey("schedule.id"))
    cash_register_id = Column(Integer, ForeignKey("cash_registers.id"))
    company_id = Column(Integer, ForeignKey("companies.id"))
    created_by = Column(Integer, ForeignKey("users.id"))

    cash_register = relationship("CashRegister", back_populates="transactions")
    schedule = relationship("Schedule")
    company = relationship("Company")
    created_user = relationship("User")
