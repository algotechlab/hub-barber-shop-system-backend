# src/model/employee/employee.py
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import db
from src.log.log import setup_logger

log = setup_logger()

CHECK_ROLE_EMPLOYEE = "Administrador"


class Employee(db.Model):
    __tablename__ = "employee"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(db.String(120), nullable=False)
    date_of_birth: Mapped[datetime] = mapped_column(db.DateTime, nullable=False)
    phone: Mapped[str] = mapped_column(db.String(40), nullable=False)
    role: Mapped[str] = mapped_column(db.String(40), nullable=False)
    session_token: Mapped[str] = mapped_column(db.Text, nullable=True)
    password: Mapped[str] = mapped_column(db.String(300), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[str] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(
        db.DateTime, nullable=True, server_default=func.now()
    )
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)

    def __repr__(self):
        return f"""{self.username} created employeesuccessfully"""
