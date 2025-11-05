# src/model/schedule/block.py

from datetime import datetime

from sqlalchemy import ForeignKey, select, text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import db
from src.log.log import setup_logger
from src.model.model import Employee
from src.utils.metadata import Metadata

log = setup_logger()


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

    @classmethod
    def add_block_schedule(
        cls,
        start_time: datetime,
        end_time: datetime,
        employee_id: int,
    ):
        try:
            new_block = cls(
                start_time=start_time,
                end_time=end_time,
                employee_id=employee_id,
                is_block=True,
            )
            db.session.add(new_block)
            db.session.commit()
            return new_block
        except Exception as e:
            db.session.rollback()
            log.error(f"Error adding block schedule: {e}")
            raise e

    @classmethod
    def list_block_schedule(cls):
        try:
            stmt = (
                select(
                    cls.id,
                    cls.start_time,
                    cls.end_time,
                    cls.employee_id,
                )
                .join(
                    Employee,
                    cls.employee_id == Employee.id,
                )
                .where(
                    cls.is_block == True,
                    cls.is_deleted == False,
                )
                .order_by(cls.id)
            )
            result = db.session.execute(stmt).fetchall()
            return Metadata(result).model_to_list()
        except Exception as e:
            log.error(f"Error listing block schedule: {e}")
            raise e

    @classmethod
    def delete_block_schedule(cls, block_id: int):
        try:
            stmt = select(cls).where(
                cls.id == block_id,
                cls.is_block == True,
                cls.is_deleted == False,
            )
            block = db.session.execute(stmt).scalar_one_or_none()
            block.is_deleted = True
            block.deleted_at = datetime.utcnow()
            db.session.commit()
            return block.id

        except Exception as e:
            db.session.rollback()
            log.error(f"Error deleting block schedule: {e}")
            raise e
