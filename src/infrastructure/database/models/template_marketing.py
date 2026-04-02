from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import BaseModel


class TemplateMarketingModel(BaseModel):
    __tablename__ = 'template_marketing'

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    context_template: Mapped[str] = mapped_column(JSONB, nullable=False)
    company_id: Mapped[UUID] = mapped_column(ForeignKey('company.id'), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
