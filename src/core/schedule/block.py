# src/core/schedule/schedule_block.py

import traceback
from datetime import datetime

from flask import jsonify
from sqlalchemy import insert, select, update

from src.db.database import db
from src.model.schedule.block import ScheduleBlock
from src.utils.metadata import Metadata


class Block:
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.schedule_block = ScheduleBlock

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
