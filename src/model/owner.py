from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import BaseModels
from src.model.commons.status_role import OwnerStatus


class Owner(BaseModels):
    __tablename__ = "owners"

    first_name: Mapped[str] = mapped_column(nullable=False, unique=True)
    last_name: Mapped[str] = mapped_column(nullable=False, unique=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    phone_number: Mapped[str] = mapped_column(nullable=True, unique=True)
    role: Mapped[str] = mapped_column(
        nullable=False, default=OwnerStatus.ROLE_OWNER
    )
    is_active: Mapped[bool] = mapped_column(default=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
