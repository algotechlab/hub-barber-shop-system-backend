from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import DECIMAL, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import BaseModelWithEmployee


class Expense(BaseModelWithEmployee):
    company_id: Mapped[UUID] = mapped_column(
        ForeignKey('company.id'), nullable=False, index=True
    )
    employee_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey('employee.id'), nullable=True, index=True
    )
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
