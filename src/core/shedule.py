# src/core/shedule.py

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
from src.model.model import Employee, Products, SheduleService, User
from src.utils.log import logdb
from src.utils.pagination import Pagination

SHEDULE_FIELDS = [
    "product_id",
    "employee_id",
    "time_register",
]


class SheduleCore:
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.shedule = SheduleService
        self.product = Products
        self.employee = Employee
        self.user = User

    def __parser_iso_format(self, dt_str: str) -> datetime:
        if dt_str.endswith("Z"):
            dt_str = dt_str.replace("Z", "+00:00")
        return datetime.fromisoformat(dt_str)

    def add_shedule(self, data: dict):
        try:
            time_register_str = self.__parser_iso_format(
                dt_str=data.get("time_register")
            )

            stmt = insert(self.shedule).values(
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
                        "message_id": "success_add_shedule",
                        "error": False,
                    }
                ),
                200,
            )

        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error add shedule: \
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

    def list_shedule(self, data: dict):
        try:
            stmt = (
                select(
                    self.shedule.id,
                    self.employee.id.label("employee_id"),
                    self.user.id.label("user_id"),
                    self.employee.username.label("name_employee"),
                    self.product.description.label("description"),
                    self.shedule.time_register.label("time_register"),
                    func.to_char(
                        self.product.time_to_spend, "HH24:MI:SS"
                    ).label("time_to_spend"),
                    self.user.username.label("name_client"),
                    self.user.phone.label("phone"),
                    (
                        self.shedule.time_register + self.product.time_to_spend
                    ).label("end_time"),
                )
                .join(
                    self.employee, self.shedule.employee_id == self.employee.id
                )
                .join(self.product, self.shedule.product_id == self.product.id)
                .join(self.user, self.user.id == self.shedule.user_id)
                .where(~self.shedule.is_deleted)
                .where(~self.product.is_deleted)
            )

            result_raw = db.session.execute(stmt).fetchall()

            if not result_raw:
                return (
                    jsonify(
                        {
                            "status_code": 404,
                            "message_id": "shedule_not_found",
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
                        "message_id": "success_list_shedule",
                        "error": False,
                        "data": converted_result,
                    }
                ),
                200,
            )

        except Exception as e:
            logdb(
                "error",
                message=f"Error in list_shedule: \
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

    def update_shedule(self, id: int, data: dict):
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

            self.shedule = db.session.get(SheduleService, id)
            if not self.shedule:
                return (
                    jsonify(
                        {
                            "status_code": 404,
                            "message_id": "shedule_not_found",
                        }
                    ),
                    404,
                )

            for key, value in data.items():
                if value is not None and key in SHEDULE_FIELDS:
                    setattr(self.shedule, key, value)

            self.shedule.updated_by = self.user_id
            self.shedule.updated_at = datetime.now()

            db.session.commit()

            return {
                "status_code": 200,
                "message_id": "success_update_shedule",
                "error": False,
            }, 200

        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error update shedule: {e}\n{traceback.format_exc()}",
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

    def delete_shedule(self, id: int):
        try:
            stmt = (
                update(self.shedule)
                .where(~self.shedule.is_deleted, self.shedule.id == id)
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
                            "message_id": "success_delete_shedule",
                            "error": False,
                        }
                    )
                )
            ), 200

        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error delete shedule: \
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
