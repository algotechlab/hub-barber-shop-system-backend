# src/core/schedule/schedule_block.py

import traceback

from flask import jsonify

from log.log import setup_logger
from src.db.database import db
from src.model.schedule.block import ScheduleBlock

log = setup_logger()


class Block:
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.schedule_block = ScheduleBlock

    def add_block_schedule(self, data: dict):
        try:
            self.schedule_block.add_block_schedule(
                start_time=data.get("start_time"),
                end_time=data.get("end_time"),
                employee_id=data.get("employee_id"),
            )
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
            log.error(f"Error block schedule: {e}\n{traceback.format_exc()}")
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
            schedule = self.schedule_block.list_block_schedule()
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

            return jsonify(
                {
                    "status_code": 200,
                    "data": schedule,
                    "message_id": "list_block_schedule_success",
                    "error": False,
                }
            )
        except Exception as e:
            log.error(
                f"Error listing block schedule: {e}\n{traceback.format_exc()}"
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
            self.schedule_block.delete_block_schedule(id)
            return jsonify(
                {
                    "status_code": 200,
                    "message_id": "delete_block_schedule_success",
                }
            )

        except Exception as e:
            log.error(
                f"Error deleting block schedule: {e}\n{traceback.format_exc()}"
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
