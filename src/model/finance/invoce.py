# src/model/finance/invoce.py

from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import db
from src.log.log import setup_logger

log = setup_logger()


class Invoice(db.Model):
    __tablename__ = "invoice"
    __table_args__ = {"schema": "finance"}

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("public.user.id"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("public.products.id"), nullable=False
    )
    payments_id: Mapped[int] = mapped_column(
        ForeignKey("finance.payments.id"), nullable=False
    )
    schedule_id: Mapped[int] = mapped_column(
        ForeignKey("schedule.service.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)

    def __repr__(self):
        return f"""<Invoice id={self.id}"""
