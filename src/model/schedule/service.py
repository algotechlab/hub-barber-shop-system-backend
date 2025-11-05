# src/models/schedule/__init__.py


from datetime import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import db
from src.log.log import setup_logger
from src.model.model import Employee, Products, User
from src.utils.metadata import Metadata

log = setup_logger()

SCHEDULE_FIELDS = [
    "product_id",
    "employee_id",
    "time_register",
]


class ScheduleService(db.Model):
    __tablename__ = "service"
    __table_args__ = {"schema": "schedule"}

    id: Mapped[int] = mapped_column(primary_key=True)
    time_register: Mapped[datetime] = mapped_column(db.DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, nullable=False, server_default=func.now()
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

    @classmethod
    def add_schedule(
        cls,
        user_id: int,
        product_id: int,
        employee_id: int,
        time_register: datetime,
    ):
        try:
            new_schedule = cls(
                user_id=user_id,
                product_id=product_id,
                employee_id=employee_id,
                time_register=time_register,
                is_check=False,
                is_awayalone=False,
                created_at=datetime.now(),
            )
            db.session.add(new_schedule)
            db.session.commit()
            log.info(f"Schedule added successfully: {new_schedule}")
            return new_schedule
        except Exception as e:
            log.error(f"Error adding schedule: {e}")
            raise e

    @classmethod
    def get_all_services(cls, data: dict = None):
        try:
            stmt = (
                select(
                    cls.id,
                    cls.time_register,
                    Employee.id.label("employee_id"),
                    Products.id.label("product_id"),
                    Products.description.label("product_name"),
                    func.to_char(Products.time_to_spend, "HH24:MI:SS").label(
                        "time_to_spend"
                    ),
                    User.phone.label("phone"),
                    User.username.label("name_client"),
                    (cls.time_register + Products.time_to_spend).label("end_time"),
                    Employee.username.label("name_employee"),
                )
                .join(Employee, cls.employee_id == Employee.id)
                .join(Products, cls.product_id == Products.id)
                .join(User, cls.user_id == User.id)
                .where(cls.is_deleted == False)
            )

            filter_by = data.get("filter_by")
            if filter_by:
                filter_value = f"%{filter_by}%"
                stmt = stmt.filter(
                    or_(
                        func.unaccent(User.username).ilike(func.unaccent(filter_value)),
                        func.unaccent(User.username).ilike(func.unaccent(filter_value)),
                    )
                )

            result_raw = db.session.execute(stmt).fetchall()
            return Metadata(result_raw).model_to_list()

        except Exception as e:
            log.error(f"Error retrieving all services: {e}")
            raise e

    @classmethod
    def get_by_id_schedule(cls, user_id: int):
        try:
            stmt = (
                select(
                    cls.id,
                    cls.time_register,
                    Employee.id.label("employee_id"),
                    Products.id.label("product_id"),
                    Products.description.label("product_name"),
                    func.to_char(Products.time_to_spend, "HH24:MI:SS").label(
                        "time_to_spend"
                    ),
                    User.phone.label("phone"),
                    User.username.label("name_client"),
                    (cls.time_register + Products.time_to_spend).label("end_time"),
                    Employee.username.label("name_employee"),
                )
                .join(Employee, cls.employee_id == Employee.id)
                .join(Products, cls.product_id == Products.id)
                .join(User, cls.user_id == User.id)
                .where(
                    cls.is_deleted == False,
                    cls.user_id == user_id,
                    cls.is_check == True,
                )
            )
            result_raw = db.session.execute(stmt).fetchall()
            return Metadata(result_raw).model_to_list()

        except Exception as e:
            log.error(f"Error retrieving schedule by ID: {e}")
            raise e

    @classmethod
    def check_schedule(cls, schedule_id: int):
        try:
            schedule = db.session.query(cls).filter_by(id=schedule_id).first()

            if schedule_id:
                schedule.is_check = True
                db.session.commit()
                return schedule.id
            else:
                log.error(f"Schedule with ID {schedule_id} not found.")
                raise ValueError(f"Schedule with ID {schedule_id} not found.")

        except Exception as e:
            log.error(f"Error checking schedule: {e}")
            db.session.rollback()
            raise e

    @classmethod
    def update_schedule(cls, schedule_id: int, data: dict):
        try:
            schedule = db.session.query(cls).filter_by(id=schedule_id).first()

            if not schedule:
                log.error(f"Schedule with ID {schedule_id} not found.")
                raise ValueError(f"Schedule with ID {schedule_id} not found.")

            for key, value in data.items():
                if value is not None and key in SCHEDULE_FIELDS:
                    setattr(schedule, key, value)

            schedule.updated_at = datetime.now()
            db.session.add(schedule)
            db.session.commit()
            return schedule

        except Exception as e:
            log.error(f"Error updating schedule: {e}")
            db.session.rollback()
            raise e

    @classmethod
    def delete_schedule(cls, schedule_id: int):
        try:
            schedule = db.session.query(cls).filter_by(id=schedule_id).first()

            if not schedule:
                log.error(f"Schedule with ID {schedule_id} not found.")
                raise ValueError(f"Schedule with ID {schedule_id} not found.")

            schedule.is_deleted = True
            db.session.commit()
            return schedule.id

        except Exception as e:
            log.error(f"Error deleting schedule: {e}")
            db.session.rollback()
            raise e
