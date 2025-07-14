# src/core/schedule.py

import traceback
from datetime import datetime

from flask import jsonify
from sqlalchemy import insert, select, update

from src.db.database import db
from src.log.log import setup_logger
from src.model.schedule.service import ScheduleService
from src.utils.log import logdb
from src.utils.metadata import Metadata

log = setup_logger()


SCHEDULE_FIELDS = [
    "product_id",
    "employee_id",
    "time_register",
]


class ServiceCore:
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.schedule = ScheduleService
        # self.block_schedule_service = ScheduleBlock # TODO refatorar

    def add_schedule(self, data: dict):
        try:
            user_id = data.get("user_id")
            product_id = data.get("product_id")
            employee_id = data.get("employee_id")
            time_register = data.get("time_register")

            self.schedule.add_schedule(
                user_id=user_id,
                product_id=product_id,
                employee_id=employee_id,
                time_register=time_register,
            )

            return (
                jsonify(
                    {
                        "status_code": 200,
                        "message_id": "success_add_schedule",
                        "error": False,
                        "message": "Schedule added successfully",
                    }
                ),
                200,
            )

        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error add schedule: {e}{traceback.format_exc()}",
            )
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "something_went_wrong",
                        "traceback": traceback.format_exc(),
                        "error": True,
                        "message": "Failed to add schedule",
                    }
                ),
                500,
            )

    def list_schedule(self, data: dict):
        try:
            schedule = self.schedule.get_all_services(data)
            if not schedule:
                return (
                    jsonify(
                        {
                            "status_code": 404,
                            "message_id": "schedule_not_found",
                            "error": True,
                        }
                    ),
                    404,
                )

            return (
                jsonify(
                    {
                        "status_code": 200,
                        "message_id": "success_list_schedule",
                        "error": False,
                        "data": schedule,
                    }
                ),
                200,
            )

        except Exception as e:
            db.session.rollback()
            log.error(f"Error in list_schedule: {e}")
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
            schedule = self.schedule.get_by_id_schedule(user_id=self.user_id)
            if not schedule:
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

            return (
                jsonify(
                    {
                        "status_code": 200,
                        "message_id": "success_list_schedule",
                        "error": False,
                        "data": schedule,
                    }
                ),
                200,
            )

        except Exception as e:
            db.session.rollback()
            log.error(f"Error in get_schedule: {e}")
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

    def check_schedule(self, id: int, data: dict):
        try:
            schedule_check = (
                update(self.schedule)
                .where(self.schedule.id == id)
                .values(is_check=True)
                .returning(self.schedule.id)
            )

            schedule_result = db.session.execute(schedule_check)
            schedule_id = schedule_result.scalar()

            check_tip = data.get("tip", 0)
            check_value_operation = data.get("value_operation", 0)

            invoice_stmt = (
                insert(self.invoice)
                .values(
                    product_id=data.get("product_id"),
                    payments_id=data.get("payment_id"),
                    schedule_id=schedule_id,
                    user_id=data.get("user_id"),
                )
                .returning(self.invoice.id)
            )

            invoice_result = db.session.execute(invoice_stmt)
            invoice_id = invoice_result.scalar()
            db.session.commit()

            box_accounting = insert(self.box_accounting).values(
                value_operation=check_value_operation,
                invoice_id=invoice_id,
                tip=check_tip,
            )
            db.session.execute(box_accounting)
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
                if value is not None and key in SCHEDULE_FIELDS:
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

    def add_block_schedule(self, data: dict):
        try:
            stmt = insert(self.block_schedule_service).values(
                time_register=data.get("time_register"),
                employee_id=data.get("employee_id"),
                time_block=data.get("duration"),
                is_block=True,
            )
            db.session.execute(stmt)
            db.session.commit()
            return (
                jsonify(
                    {
                        "status_code": 200,
                        "message_id": "success_block_schedule",
                        "error": False,
                    }
                ),
                200,
            )

        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error block schedule: \
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

    def list_block_schedule(self):
        try:
            stmt = (
                select(
                    self.block_schedule_service.id,
                    self.block_schedule_service.start_time,
                    self.block_schedule_service.end_time,
                    self.employee.id.label("employee_id"),
                    self.employee.username.label("name_employee"),
                )
                .join(
                    self.employee,
                    self.block_schedule_service.employee_id
                    == self.employee.id,
                )
                .where(
                    self.block_schedule_service.is_block == True,
                    self.block_schedule_service.is_deleted == False,
                )
                .order_by(self.block_schedule_service.id)
            )

            result = db.session.execute(stmt).fetchall()

            if not result:
                return (
                    jsonify(
                        {
                            "status_code": 404,
                            "message_id": "schedule_not_found",
                            "error": True,
                        }
                    ),
                    404,
                )

            return jsonify(
                {
                    "status_code": 200,
                    "data": Metadata(result).model_to_list(),
                    "message_id": "list_block_schedule_success",
                    "error": False,
                }
            )
        except Exception as e:
            print("Coletando o meu erro", e)
            logdb(
                "error",
                message=f"Error list block schedule: \
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

    def delete_block_schedule(self, id: int):
        try:
            stmt = (
                update(self.block_schedule_service)
                .where(
                    ~self.block_schedule_service.is_deleted,
                    self.block_schedule_service.id == id,
                )
                .values(
                    deleted_by=self.user_id,
                    deleted_at=datetime.now(),
                    is_deleted=True,
                    is_block=False,
                )
            )

            db.session.execute(stmt)
            db.session.commit()

            return jsonify(
                {
                    "status_code": 200,
                    "message_id": "delete_block_schedule_success",
                }
            )

        except Exception as e:
            print("Error coletado", e)
            logdb(
                "error",
                message=f"Error list block schedule: \
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
