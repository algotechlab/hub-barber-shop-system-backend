from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import BaseModels


class User(BaseModels):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    phone: Mapped[str] = mapped_column(nullable=False, unique=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"), nullable=False
    )

    def __repr__(self):
        return (
            f"<User id={self.id} "
            f"username={self.username} "
            f"email={self.email} "
            f"phone={self.phone}>"
        )
