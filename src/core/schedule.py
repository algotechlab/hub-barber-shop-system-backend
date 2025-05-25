# src/core/schedule.py

import traceback
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import jsonify
from sqlalchemy import (
    func,
    insert,
    or_,
    select,
    update,
)

from src.db.database import db
from src.model.model import Employee, Products, ScheduleService, User
from src.utils.log import logdb

schedule_FIELDS = [
    "product_id",
    "employee_id",
    "time_register",
]


class ScheduleCore:
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.schedule = ScheduleService
        self.product = Products
        self.employee = Employee
        self.user = User

    def __parser_iso_format(self, dt_str: str) -> datetime:
        if dt_str.endswith("Z"):
            dt_str = dt_str.replace("Z", "+00:00")
        return datetime.fromisoformat(dt_str)

    def add_schedule(self, data: dict):
        try:
            time_register_str = self.__parser_iso_format(
                dt_str=data.get("time_register")
            )

            stmt = insert(self.schedule).values(
                product_id=data.get("product_id"),
                employee_id=data.get("employee_id"),
                time_register=time_register_str,
                user_id=data.get("user_id"),
                is_awayalone=False,
                is_check=False,
            )
            db.session.execute(stmt)
            db.session.commit()

            return (
                jsonify(
                    {
                        "status_code": 200,
                        "message_id": "success_add_schedule",
                        "error": False,
                    }
                ),
                200,
            )

        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error add schedule: \
                {e}{traceback.format_exc()}",
            )
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "something_went_wrong",
                        "traceback": traceback.format_exc(),
                    }
                ),
                500,
            )

    def list_schedule(self, data: dict):
        try:
            stmt = (
                select(
                    self.schedule.id,
                    self.employee.id.label("employee_id"),
                    self.user.id.label("user_id"),
                    self.employee.username.label("name_employee"),
                    self.product.description.label("description"),
                    self.schedule.time_register.label("time_register"),
                    func.to_char(
                        self.product.time_to_spend, "HH24:MI:SS"
                    ).label("time_to_spend"),
                    self.user.username.label("name_client"),
                    self.user.phone.label("phone"),
                    (
                        self.schedule.time_register
                        + self.product.time_to_spend
                    ).label("end_time"),
                )
                .join(
                    self.employee,
                    self.schedule.employee_id == self.employee.id,
                )
                .join(
                    self.product, self.schedule.product_id == self.product.id
                )
                .join(self.user, self.user.id == self.schedule.user_id)
                .where(~self.schedule.is_deleted)
                .where(~self.schedule.is_check)
                .where(~self.product.is_deleted)
            )

            filter_by = data.get("filter_by")
            if filter_by:
                filter_value = f"%{filter_by}%"
                stmt = stmt.filter(
                    or_(
                        func.unaccent(self.employee.username).ilike(
                            func.unaccent(filter_value)
                        ),
                        func.unaccent(self.user.username).ilike(
                            func.unaccent(filter_value)
                        ),
                    )
                )

            result_raw = db.session.execute(stmt).fetchall()

            if not result_raw:
                return (
                    jsonify(
                        {
                            "status_code": 404,
                            "message_id": "schedule_not_found",
                            "error": False,
                        }
                    ),
                    404,
                )

            converted_result = []
            for row in result_raw:
                row_dict = dict(row._mapping)
                time_register = row_dict.get("time_register")
                end_time = row_dict.get("end_time")

                # Formatar time_register
                if time_register and isinstance(time_register, datetime):
                    if time_register.tzinfo is None:
                        time_register = time_register.replace(
                            tzinfo=ZoneInfo("UTC")
                        )
                    row_dict["time_register"] = time_register.astimezone(
                        ZoneInfo("America/Sao_Paulo")
                    ).strftime("%d-%m-%Y %H:%M:%S")

                # Formatar end_time
                if end_time and isinstance(end_time, datetime):
                    if end_time.tzinfo is None:
                        end_time = end_time.replace(tzinfo=ZoneInfo("UTC"))
                    row_dict["end_time"] = end_time.astimezone(
                        ZoneInfo("America/Sao_Paulo")
                    ).strftime("%d-%m-%Y %H:%M:%S")

                converted_result.append(row_dict)

            return (
                jsonify(
                    {
                        "status_code": 200,
                        "message_id": "success_list_schedule",
                        "error": False,
                        "data": converted_result,
                    }
                ),
                200,
            )

        except Exception as e:
            logdb(
                "error",
                message=f"Error in list_schedule: \
                {str(e)}\n{traceback.format_exc()}",
            )
            db.session.rollback()
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "internal_server_error",
                        "error": str(e),
                    }
                ),
                500,
            )

    def get_schedule(self):
        try:
            stmt = (
                select(
                    self.schedule.id,
                    self.employee.id.label("employee_id"),
                    self.user.id.label("user_id"),
                    self.employee.username.label("name_employee"),
                    self.product.description.label("description"),
                    self.schedule.time_register.label("time_register"),
                    func.to_char(
                        self.product.time_to_spend, "HH24:MI:SS"
                    ).label("time_to_spend"),
                    self.user.username.label("name_client"),
                    self.user.phone.label("phone"),
                    (
                        self.schedule.time_register
                        + self.product.time_to_spend
                    ).label("end_time"),
                )
                .join(
                    self.employee,
                    self.schedule.employee_id == self.employee.id,
                )
                .join(
                    self.product, self.schedule.product_id == self.product.id
                )
                .join(self.user, self.user.id == self.schedule.user_id)
                .where(~self.schedule.is_deleted)
                .where(~self.schedule.is_check)
                .where(~self.product.is_deleted)
                .where(self.user_id == self.schedule.user_id)
            )
            result_raw = db.session.execute(stmt).fetchall()

            if not result_raw:
                return (
                    jsonify(
                        {
                            "status_code": 404,
                            "message_id": "schedule_not_found",
                            "error": False,
                        }
                    ),
                    404,
                )
            converted_result = []
            for row in result_raw:
                row_dict = dict(row._mapping)
                time_register = row_dict.get("time_register")
                end_time = row_dict.get("end_time")

                # Formatar time_register
                if time_register and isinstance(time_register, datetime):
                    if time_register.tzinfo is None:
                        time_register = time_register.replace(
                            tzinfo=ZoneInfo("UTC")
                        )
                    row_dict["time_register"] = time_register.astimezone(
                        ZoneInfo("America/Sao_Paulo")
                    ).strftime("%d-%m-%Y %H:%M:%S")

                # Formatar end_time
                if end_time and isinstance(end_time, datetime):
                    if end_time.tzinfo is None:
                        end_time = end_time.replace(tzinfo=ZoneInfo("UTC"))
                    row_dict["end_time"] = end_time.astimezone(
                        ZoneInfo("America/Sao_Paulo")
                    ).strftime("%d-%m-%Y %H:%M:%S")

                converted_result.append(row_dict)

            return (
                jsonify(
                    {
                        "status_code": 200,
                        "message_id": "success_list_schedule",
                        "error": False,
                        "data": converted_result,
                    }
                ),
                200,
            )

        except Exception as e:
            logdb(
                "error",
                message=f"Error in get_schedule: \
                {str(e)}\n{traceback.format_exc()}",
            )
            db.session.rollback()
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "internal_server_error",
                        "error": str(e),
                    }
                ),
                500,
            )

    def check_schedule(self, id: int):
        try:
            stmt = (
                update(self.schedule)
                .where(self.schedule.id == id)
                .values(is_check=True)
            )
            db.session.execute(stmt)
            db.session.commit()

            return (
                jsonify(
                    {
                        "status_code": 200,
                        "message_id": "success_check_schedule",
                        "error": False,
                    }
                ),
                200,
            )

        except Exception as e:
            logdb(
                "error",
                message=f"Error in check_schedule: \
                {str(e)}\n{traceback.format_exc()}",
            )
            db.session.rollback()
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "internal_server_error",
                        "error": str(e),
                    }
                ),
                500,
            )

    def update_schedule(self, id: int, data: dict):
        try:
            if not id:
                return (
                    jsonify(
                        {
                            "status_code": 400,
                            "message_id": "id_is_required",
                        }
                    ),
                    400,
                )

            self.schedule = db.session.get(ScheduleService, id)
            if not self.schedule:
                return (
                    jsonify(
                        {
                            "status_code": 404,
                            "message_id": "schedule_not_found",
                        }
                    ),
                    404,
                )

            for key, value in data.items():
                if value is not None and key in schedule_FIELDS:
                    setattr(self.schedule, key, value)

            self.schedule.updated_by = self.user_id
            self.schedule.updated_at = datetime.now()

            db.session.commit()

            return {
                "status_code": 200,
                "message_id": "success_update_schedule",
                "error": False,
            }, 200

        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error update schedule: \
                {e}\n{traceback.format_exc()}",
            )
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "something_went_wrong",
                        "traceback": traceback.format_exc(),
                    }
                ),
                500,
            )

    def delete_schedule(self, id: int):
        try:
            stmt = (
                update(self.schedule)
                .where(~self.schedule.is_deleted, self.schedule.id == id)
                .values(
                    deleted_by=self.user_id,
                    deleted_at=datetime.now(),
                    is_deleted=True,
                )
            )

            db.session.execute(stmt)
            db.session.commit()

            return (
                jsonify(
                    (
                        {
                            "status_code": 200,
                            "message_id": "success_delete_schedule",
                            "error": False,
                        }
                    )
                )
            ), 200

        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error delete schedule: \
                {e}{traceback.format_exc()}",
            )
            return (
                jsonify(
                    (
                        {
                            "status_code": 500,
                            "message_id": "something_went_wrong",
                            "traceback": traceback.format_exc(),
                        },
                    )
                ),
                500,
            )()
