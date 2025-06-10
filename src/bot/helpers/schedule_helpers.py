from zoneinfo import ZoneInfo
from datetime import date, time, timedelta
from datetime import datetime
from sqlalchemy.orm import aliased
from sqlalchemy import insert, select, func, or_, and_, exists
from src.bot.response_dictionary import RESPONSE_DICTIONARY
from src.db.database import db
from src.model.model import User, Employee, ScheduleService, Products
from src.service.redis import SessionManager
from src.utils.log import logdb
from src.utils.metadata import Metadata


class HelpersScheduler:
    def __init__(self, send_number: str, *args, **kwargs):
        self.session = SessionManager()
        self.sender_number = send_number

    def identify_user(self):
        try:
            stmt = select(User.id).where(User.phone == self.sender_number)
            result = db.session.execute(stmt).fetchone()
            return result[0] if result else None
        except Exception as e:
            logdb("error", message=f"Failed to identify user: {e}")
            return None

    def list_available_employees(self, hour: datetime):
        try:
            if hour.tzinfo is None:
                hour = hour.replace(tzinfo=ZoneInfo("America/Sao_Paulo"))

            hour_utc = hour.astimezone(ZoneInfo("UTC"))

            ScheduleAlias = aliased(ScheduleService)
            ProductAlias = aliased(Products)
            EmployeeAlias = aliased(Employee)

            subq = (
                select(
                    ScheduleAlias.employee_id.label("employee_id"),
                    ScheduleAlias.time_register.label("inicio"),
                    (
                        ScheduleAlias.time_register
                        + ProductAlias.time_to_spend
                    ).label("fim"),
                )
                .join(
                    ProductAlias, ScheduleAlias.product_id == ProductAlias.id
                )
                .where(ScheduleAlias.is_deleted.is_(False))
                .where(ScheduleAlias.is_check.is_(False))
                .where(ProductAlias.is_deleted.is_(False))
                .subquery()
            )

            stmt = (
                select(EmployeeAlias.id, EmployeeAlias.username)
                .where(EmployeeAlias.is_deleted.is_(False))
                .where(
                    ~exists().where(
                        and_(
                            subq.c.employee_id == EmployeeAlias.id,
                            subq.c.inicio <= hour_utc,
                            hour_utc < subq.c.fim,
                        )
                    )
                )
                .order_by(EmployeeAlias.username)
            )

            result = db.session.execute(stmt).fetchall()

            if not result:
                logdb("warning", message="Not found")

            employees = [{"id": row[0], "username": row[1]} for row in result]
            return employees
        except Exception as e:
            logdb("error", message=f"Error list employees: {e}")

    def register_schedule(
        self,
        user_id: int,
        product_id: int,
        employee_id: int,
        datetime_obj: datetime,
    ):
        try:
            stmt = insert(ScheduleService).values(
                product_id=int(product_id),
                employee_id=int(employee_id),
                user_id=user_id,
                time_register=datetime_obj,
                is_awayalone=False,
                is_check=True,
            )
            db.session.execute(stmt)
            db.session.commit()
            return self.session.reset_to_default(
                self.sender_number,
                {
                    "success": (
                        "✅ Agendamento realizado com sucesso!\n\n"
                        + RESPONSE_DICTIONARY["default"]
                    )
                },
            )
        except Exception as e:
            db.session.rollback()
            logdb("error", message=f"Failed to save schedule: {e}")
            return self.session.reset_to_default(
                self.sender_number,
                {
                    "error": (
                        "Erro ao realizar agendamento. Tente novamente.\n\n"
                        + RESPONSE_DICTIONARY["default"]
                    )
                },
            )

    def list_slots_employees(self):
        try:
            local_tz = ZoneInfo("America/Sao_Paulo")
            start = datetime.combine(date.today(), time(8, 0, tzinfo=local_tz))
            end = datetime.combine(date.today(), time(23, 0, tzinfo=local_tz))
            step = timedelta(minutes=20)

            hour_slots = {"manhã": [], "tarde": [], "noite": []}

            while start <= end:
                available_employees = self.list_available_employees(hour=start)

                if available_employees:
                    time_str = start.strftime("%H:%M")
                    period = (
                        "manhã"
                        if start.hour < 12
                        else "tarde"
                        if start.hour < 18
                        else "noite"
                    )
                    hour_slots[period].append(time_str)

                start += step

            return hour_slots
        except Exception as e:
            logdb("error", message=f"Failed to list slots: {e}")
            return None

    def validate_employee(self, employee_id: int) -> bool:
        try:
            stmt = select(Employee.id).where(
                Employee.id == employee_id, ~Employee.is_deleted
            )
            return db.session.execute(stmt).scalar() is not None
        except Exception as e:
            logdb("error", message=f"Failed to validate employee: {e}")
            return False

    def validate_product(self, product_id: int) -> bool:
        try:
            stmt = select(Products.id).where(
                Products.id == product_id, ~Products.is_deleted
            )
            return db.session.execute(stmt).scalar() is not None
        except Exception as e:
            logdb("error", message=f"Failed to validate product: {e}")
            return False

    def get_employees(self):
        try:
            stmt = select(Employee.id, Employee.username).where(
                ~Employee.is_deleted
            )
            result = db.session.execute(stmt).fetchall()
            metadata = Metadata(result).model_to_list()
            return "\n".join(
                [f"{item['id']} - {item['username']}" for item in metadata]
            )
        except Exception as e:
            logdb("error", message=f"Failed to get employees: {e}")
            return ""

    def get_products(self):
        try:
            stmt = select(
                Products.id, func.upper(Products.description).label("name")
            ).where(~Products.is_deleted)
            result = db.session.execute(stmt).fetchall()
            metadata = Metadata(result).model_to_list()
            return "\n".join(
                [f"{item['id']} - {item['name']}" for item in metadata]
            )
        except Exception as e:
            logdb("error", message=f"Failed to get products: {e}")
            return ""
