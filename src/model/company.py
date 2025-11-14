from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import BaseModels


class Company(BaseModels):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    email: Mapped[str] = mapped_column(nullable=True)
    phone_number: Mapped[str] = mapped_column(nullable=True, unique=True)
    color: Mapped[str] = mapped_column(nullable=True)
    slug: Mapped[str] = mapped_column(nullable=False, unique=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("owners.id"), nullable=False
    )
