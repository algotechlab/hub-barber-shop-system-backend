from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import BaseModels


class ProductsEmployees(BaseModels):
    __tablename__ = "products_employees"

    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.id"), nullable=False
    )
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id"), nullable=False
    )
    is_check: Mapped[bool] = mapped_column(Boolean, default=False)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"), nullable=False
    )
