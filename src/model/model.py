# src/model/model.py
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import db


class Log(db.Model):
    __tablename__ = "logs"
    __table_args__ = {'schema': 'audit_logs'}
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, server_default=func.now())
    logger_name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    level: Mapped[str] = mapped_column(db.String(100), nullable=False)
    message: Mapped[str] = mapped_column(db.Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, server_default=func.now())
    
    def __repr__(self):
        return f"<Log: Loggin registred at {self.timestamp} - {self.logger_name} - {self.level} - {self.message}>"

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(120), nullable=False)
    email: Mapped[str] = mapped_column(db.String(100), nullable=False)
    password: Mapped[str] = mapped_column(db.String(300), nullable=False)
    phone: Mapped[str] = mapped_column(db.String(40), nullable=False)
    created_at: Mapped[str] = mapped_column(db.DateTime, nullable=False)
    updated_at: Mapped[str] = mapped_column(db.DateTime, nullable=False)
    updated_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    deleted_by: Mapped[int] = mapped_column(db.Integer, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)

    def __repr__(self):
        return f"""{self.name} created successfully"""
