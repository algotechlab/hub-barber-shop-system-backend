# src/core/schedule.py

import traceback

from flask import jsonify
from sqlalchemy import insert, update

from src.db.database import db
from src.log.log import setup_logger
from src.model.schedule.service import ScheduleService
from src.utils.log import logdb

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
        # todo - esse metedo ira para o finance
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
            self.schedule.update_schedule(id, data)
            return {
                "status_code": 200,
                "message_id": "success_update_schedule",
                "error": False,
            }, 200

        except Exception as e:
            db.session.rollback()
            log.error(f"Error updating schedule: {e}")
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
            self.schedule.delete_schedule(id)
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
            )
