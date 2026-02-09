from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import BaseModel


class BranchCompany(BaseModel):
    name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    company_id: Mapped[UUID] = mapped_column(ForeignKey('company.id'), nullable=False)
