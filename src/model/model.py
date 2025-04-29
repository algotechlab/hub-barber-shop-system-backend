# src/model/model.py
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import db


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
