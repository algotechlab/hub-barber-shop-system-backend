# src/model/schedule/block.py

# TODO - crud refatoração schedule block

from datetime import datetime

from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import db


class ScheduleBlock(db.Model):
    __tablename__ = "block"
    __table_args__ = {"schema": "schedule"}

    id: Mapped[int] = mapped_column(primary_key=True)

    start_time: Mapped[datetime] = mapped_column(db.DateTime)
    end_time: Mapped[datetime] = mapped_column(db.DateTime)

    employee_id: Mapped[int] = mapped_column(
        db.Integer, ForeignKey("public.employee.id")
    )

    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, nullable=False, server_default=text("now()")
    )

    updated_at: Mapped[datetime] = mapped_column(db.DateTime)
    updated_by: Mapped[int] = mapped_column(db.Integer)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime)
    deleted_by: Mapped[int] = mapped_column(db.Integer)

    is_block: Mapped[bool] = mapped_column(
        db.Boolean, server_default=text("false"), nullable=False
    )

    is_deleted: Mapped[bool] = mapped_column(
        db.Boolean, server_default=text("false"), nullable=False
    )
