from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import BaseModels


class Employee(BaseModels):
    __tablename__ = "employees"

    first_name: Mapped[str] = mapped_column(nullable=False, unique=True)
    last_name: Mapped[str] = mapped_column(nullable=False, unique=True)
    phone_number: Mapped[str] = mapped_column(nullable=True, unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    session_token: Mapped[str] = mapped_column(nullable=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"), nullable=False
    )
