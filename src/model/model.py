# src/model/model.py
from datetime import datetime

from sqlalchemy import Interval, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import db


class Log(db.Model):
    __tablename__ = "logs"
    __table_args__ = {"schema": "audit_logs"}

    id: Mapped[int] = mapped_column(
        db.Integer, primary_key=True, autoincrement=True
    )
    timestamp: Mapped[datetime] = mapped_column(
        db.DateTime, nullable=False, server_default=func.now()
    )
    logger_name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    level: Mapped[str] = mapped_column(db.String(100), nullable=False)
    message: Mapped[str] = mapped_column(db.Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, nullable=False, server_default=func.now()
    )

    def __repr__(self):
        return (
            f"<Log: Loggin registred at {self.timestamp} - "
            f"{self.logger_name} - {self.level} - {self.message}>"
        )


class User(db.Model):
    __tablename__ = "user"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(db.String(120), nullable=False)
    lastname: Mapped[str] = mapped_column(db.String(120), nullable=False)
    email: Mapped[str] = mapped_column(
        db.String(100), unique=True, nullable=False
    )
    role: Mapped[str] = mapped_column(db.String(20), nullable=False)
    password: Mapped[str] = mapped_column(db.String(300), nullable=False)
    phone: Mapped[str] = mapped_column(db.String(40), nullable=False)
    session_token: Mapped[str] = mapped_column(db.Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[str] = mapped_column(db.DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)

    def __repr__(self):
        return f"""{self.username} created successfully"""


class Employee(db.Model):
    __tablename__ = "employee"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(db.String(120), nullable=False)
    cpf: Mapped[str] = mapped_column(
        db.String(20), unique=True, nullable=False
    )
    rg: Mapped[str] = mapped_column(db.String(20), unique=True, nullable=False)
    date_of_birth: Mapped[datetime] = mapped_column(
        db.DateTime, nullable=False
    )
    nickname: Mapped[str] = mapped_column(db.String(150), nullable=True)
    email: Mapped[str] = mapped_column(
        db.String(100), unique=True, nullable=False
    )
    phone: Mapped[str] = mapped_column(db.String(40), nullable=False)
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


class Products(db.Model):
    __tablename__ = "products"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(db.String(30), nullable=False)
    value_operation: Mapped[Numeric] = mapped_column(
        db.Numeric(2, 10), default=0.00
    )
    time_to_spend: Mapped[Interval] = mapped_column(Interval, nullable=False)
    commission: Mapped[float] = mapped_column(db.Float, nullable=False)
    category: Mapped[str] = mapped_column(db.String(20), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)

    def __repr__(self):
        return f"""{self.description} created successfully"""


class SheduleService(db.Model):
    __tablename__ = "schedule_service"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True)
    time_register: Mapped[datetime] = mapped_column(
        db.DateTime, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    product_id: Mapped[int] = mapped_column(db.Integer, nullable=False)
    employee_id: Mapped[int] = mapped_column(db.Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(db.Integer, nullable=False)
    is_check: Mapped[int] = mapped_column(db.Boolean, nullable=False)
    is_awayalone: Mapped[int] = mapped_column(db.Boolean, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)

    def __repr__(self):
        return f"""{self.id} created successfully"""
