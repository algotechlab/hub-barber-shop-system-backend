# src/resource/schedule.py

import traceback

from flask import jsonify, request
from flask_cors import cross_origin
from flask_restx import Namespace, Resource, fields, reqparse

from src.core.schedule.block import Block
from src.core.schedule.service import ServiceCore

pagination_arguments_schedule = reqparse.RequestParser()
pagination_arguments_schedule.add_argument(
    "filter_by", help="Filter By", default="", type=str, required=False
)

schedule_ns = Namespace("schedule", description="Manager schedule")


payload_add_schedule = schedule_ns.model(
    "scheduleAddPayload",
    {
        "product_id": fields.Integer(required=True, description="Product id"),
        "employee_id": fields.Integer(required=True, description="Employee id"),
        "user_id": fields.Integer(required=True, description="User id"),
        "time_register": fields.DateTime(
            required=True, description="2025-07-14 08:30:00"
        ),
    },
)


payload_update_schedule = schedule_ns.model(
    "scheduleUpdatePayload",
    {
        "product_id": fields.Integer(required=False, description="Product id"),
        "employee_id": fields.Integer(required=False, description="Employee id"),
        "time_register": fields.DateTime(
            required=False, description="Time register time spent in HH:MM:SS"
        ),
    },
)

payload_check_schedule = schedule_ns.model(
    "CheckSchedule",
    {
        "product_id": fields.Integer(required=True, description="Invoice id"),
        "payment_id": fields.Integer(required=True, description="Payment id"),
        "user_id": fields.Integer(required=True, description="User id"),
        "value_operation": fields.Float(required=False, description="Operation value"),
        "tip": fields.Float(required=False, description="Tip"),
    },
)

paylaod_add_block = schedule_ns.model(
    "BlockSchedule",
    {
        "employee_id": fields.Integer(required=True, description="Employee id"),
        "duration": fields.DateTime(
            required=True, description="Duration block schedule"
        ),
        "time_register": fields.DateTime(
            required=True, description="Time register time spent in HH:MM:SS"
        ),
    },
)


@schedule_ns.route("")
class scheduleManageResource(Resource):
    @schedule_ns.doc(description="Add schedule")
    @schedule_ns.expect(payload_add_schedule, validate=True)
    @cross_origin()
    def post(self):
        """Add schedule"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return ServiceCore(user_id=user_id).add_schedule(data=request.get_json())
        except Exception:
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

    @schedule_ns.doc(description="List schedule")
    @schedule_ns.expect(pagination_arguments_schedule, validate=True)
    @cross_origin()
    def get(self):
        """List schedule"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return ServiceCore(user_id=user_id).list_schedule(
                data=request.args.to_dict()
            )
        except Exception:
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


@schedule_ns.route("/<int:id>")
class scheduleManagerResourceId(Resource):
    @schedule_ns.doc(description="Check schedule")
    @schedule_ns.expect(payload_check_schedule, validate=True)
    @cross_origin()
    def post(self, id: int):
        """Check schedule"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return ServiceCore(user_id=user_id).check_schedule(
                id=id, data=request.get_json()
            )
        except Exception:
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "traceback": traceback.format_exc(),
                },
                500,
            )

    @schedule_ns.doc(description="Update schedule")
    @schedule_ns.expect(payload_update_schedule, validate=True)
    @cross_origin()
    def put(self, id: int):
        """Update schedule"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return ServiceCore(user_id=user_id).update_schedule(
                id=id, data=request.get_json()
            )
        except Exception:
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "traceback": traceback.format_exc(),
                },
                500,
            )

    @schedule_ns.doc(description="Delete schedule")
    @cross_origin()
    def delete(self, id: int):
        """Delete schedule"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return ServiceCore(user_id=user_id).delete_schedule(
                id=id,
            )
        except Exception:
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "traceback": traceback.format_exc(),
                },
                500,
            )


@schedule_ns.route("/manageruser")  # todo - esse endpoint vai ser alterado
class scheduleManagerUserId(Resource):
    @schedule_ns.doc(description="List schedule filter user_id logged of platform")
    @schedule_ns.expect(pagination_arguments_schedule, validate=True)
    @cross_origin()
    def get(self):
        """List schedule user_id logged of platform"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return ServiceCore(user_id=user_id).get_schedule()
        except Exception:
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


@schedule_ns.route("/block")
class BlockSheduleResoruce(Resource):
    @cross_origin()
    @schedule_ns.expect(paylaod_add_block, validate=True)
    def post(self):
        """Block shedule service"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return Block(user_id=user_id).add_block_schedule(data=request.get_json())
        except Exception:
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

    @cross_origin()
    def get(self):
        """List block schedule"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return Block(user_id=user_id).list_block_schedule()
        except Exception:
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


@schedule_ns.route("/block/<int:id>")
class BlockScheduleResourceId(Resource):
    @cross_origin()
    def delete(self, id: int):
        """Delete block schedule"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return Block(user_id=user_id).delete_block_schedule(
                id=id,
            )
        except Exception:
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "traceback": traceback.format_exc(),
                },
                500,
            )
