from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import BaseModels


class Employee(BaseModels):
    __tablename__ = "employees"

    first_name: Mapped[str] = mapped_column(nullable=False, unique=True)
    last_name: Mapped[str] = mapped_column(nullable=False, unique=True)
    phone_number: Mapped[str] = mapped_column(nullable=True, unique=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"), nullable=False
    )

    def __repr__(self):
        return (
            f"<Employee id={self.id} "
            f"first_name={self.first_name} "
            f"last_name={self.last_name} "
            f"phone_number={self.phone_number} "
            f"is_active={self.is_active} "
            f"company_id={self.company_id}>"
        )
