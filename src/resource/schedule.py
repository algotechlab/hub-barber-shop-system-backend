import traceback

from flask import jsonify, request
from flask_cors import cross_origin
from flask_restx import Namespace, Resource, fields, reqparse

from src.resource.commons.pagination import PaginationArguments
from src.service.schedule import ScheduleService
from src.service.schedule_block import BlockService
from src.service.slots import SlotsService


pagination_arguments = reqparse.RequestParser()
PaginationArguments.add_to_parser(pagination_arguments)

schedule_ns = Namespace("schedule", description="Manager schedule")


payload_add_schedule = schedule_ns.model(
    "PayloadAddSchedule",
    {
        "time_register": fields.String(
            required=True,
            example="2025-11-14T15:30:00",
            description="Data e hora do agendamento no formato ISO 8601",
        ),
        "employee_id": fields.Integer(
            required=True,
            example=10,
            description="ID do colaborador responsável pelo serviço",
        ),
        "product_id": fields.Integer(
            required=True,
            example=1,
            description="ID do produto/serviço agendado",
        ),
    },
)

payload_update_schedule = schedule_ns.model(
    "PayloadUpdateSchedule",
    {
        "time_register": fields.String(
            required=False,
            example="2025-11-14T16:00:00",
            description="Nova data e hora do agendamento",
        ),
        "employee_id": fields.Integer(
            required=False,
            example=11,
            description="Novo colaborador responsável",
        ),
        "product_id": fields.Integer(
            required=False,
            example=2,
            description="Novo produto/serviço agendado",
        ),
    },
)


payload_add_schedule_block = schedule_ns.model(
    "PayloadAddScheduleBlock",
    {
        "start_time": fields.String(
            required=True,
            example="2025-11-14T09:00:00",
            description="Data e hora de início do bloqueio (ISO 8601)",
        ),
        "end_time": fields.String(
            required=True,
            example="2025-11-14T12:00:00",
            description="Data e hora de fim do bloqueio (ISO 8601)",
        ),
        "employee_id": fields.Integer(
            required=True,
            example=5,
            description="ID do colaborador que terá o horário bloqueado",
        ),
        "is_block": fields.Boolean(
            required=False,
            default=True,
            example=True,
            description="Indica se o horário está bloqueado",
        ),
        "company_id": fields.Integer(
            required=True,
            example=1,
            description="ID da empresa (multi-tenancy)",
        ),
    },
)


payload_add_schedule_block = schedule_ns.model(
    "PayloadAddScheduleBlock",
    {
        "start_time": fields.String(
            required=True,
            example="2025-11-14T09:00:00",
            description="Data e hora de início do bloqueio (ISO 8601)",
        ),
        "end_time": fields.String(
            required=True,
            example="2025-11-14T12:00:00",
            description="Data e hora de fim do bloqueio (ISO 8601)",
        ),
        "employee_id": fields.Integer(
            required=True,
            example=5,
            description="ID do colaborador que terá o horário bloqueado",
        ),
        "is_block": fields.Boolean(
            required=False,
            default=True,
            example=True,
            description="Indica se o horário está bloqueado",
        ),
    },
)


payload_slots_schedules = schedule_ns.model(
    "PayloadSlotsSchedules",
    {
        "work_start": fields.String(
            required=True,
            example="2025-11-14T09:00:00",
            description="Data e hora de início do bloqueio (ISO 8601)",
        ),
        "work_end": fields.String(
            required=True,
            example="2025-11-14T12:00:00",
            description="Data e hora de fim do bloqueio (ISO 8601)",
        ),
        "employee_id": fields.Integer(
            required=True,
            example=5,
            description="ID do colaborador que terá o horário bloqueado",
        ),
    },
)


@schedule_ns.route("")
class ScheduleResource(Resource):

    @schedule_ns.doc(description="List Schedule")
    @schedule_ns.expect(pagination_arguments, validate=True)
    @cross_origin()
    def get(self):
        """List Schedule"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            company_id = request.headers.get(
                "company_id", request.environ.get("company_id")
            )
            return ScheduleService(
                user_id=user_id, company_id=company_id
            ).list_schedule(request.args.to_dict())
        except Exception:
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "traceback": traceback.format_exc(),
                }
            )

    @schedule_ns.doc(description="Add Schedule")
    @schedule_ns.expect(payload_add_schedule, validate=True)
    @cross_origin()
    def post(self):
        """Add Schedule"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            company_id = request.headers.get(
                "company_id", request.environ.get("company_id")
            )
            return ScheduleService(
                user_id=user_id, company_id=company_id
            ).add_schedule(request.get_json())
        except Exception:
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "traceback": traceback.format_exc(),
                }
            )


@schedule_ns.route("/<int:id>")
class ScheduleFilterByUserResource(Resource):

    @schedule_ns.doc(description="Get schedule by filter user with ID")
    @cross_origin()
    def get(self, id: int):
        """Get schedule by filter user with ID"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            company_id = request.headers.get(
                "company_id", request.environ.get("company_id")
            )
            return ScheduleService(
                user_id=user_id, company_id=company_id
            ).get_schedule(id)
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


@schedule_ns.route("/<int:schedule_id>")
class ScheduleByIdResource(Resource):

    @schedule_ns.doc(description="Update schedule by ID")
    @schedule_ns.expect(payload_update_schedule, validate=True)
    @cross_origin()
    def put(self, schedule_id: int):
        """Update schedule by ID"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            company_id = request.headers.get(
                "company_id", request.environ.get("company_id")
            )
            return ScheduleService(
                user_id=user_id, company_id=company_id
            ).update_schedule(schedule_id, request.get_json())
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

    @schedule_ns.doc(description="Delete schedule by ID")
    @cross_origin()
    def delete(self, schedule_id: int):
        """Delete schedule by ID"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            company_id = request.headers.get(
                "company_id", request.environ.get("company_id")
            )
            return ScheduleService(
                user_id=user_id, company_id=company_id
            ).delete_schedule(schedule_id)
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


@schedule_ns.route("/block")
class ScheduleBlockResource(Resource):

    @schedule_ns.doc(description="Add Schedule Block")
    @schedule_ns.expect(payload_add_schedule_block, validate=True)
    @cross_origin()
    def post(self):
        """Add Schedule Block"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            company_id = request.headers.get(
                "company_id", request.environ.get("company_id")
            )
            return BlockService(
                user_id=user_id, company_id=company_id
            ).add_block(request.get_json())
        except Exception:
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "traceback": traceback.format_exc(),
                }
            )

    @schedule_ns.doc(description="List Schedule block")
    @schedule_ns.expect(pagination_arguments, validate=True)
    @cross_origin()
    def get(self):
        """List Schedule block"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            company_id = request.headers.get(
                "company_id", request.environ.get("company_id")
            )
            return BlockService(
                user_id=user_id, company_id=company_id
            ).list_blocks(request.args.to_dict())
        except Exception:
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "traceback": traceback.format_exc(),
                }
            )


@schedule_ns.route("/block/<int:block_id>")
class ScheduleBlockByResource(Resource):

    @schedule_ns.doc(description="Delete block by ID")
    @cross_origin()
    def delete(self, block_id: int):
        """Delete block by ID"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            company_id = request.headers.get(
                "company_id", request.environ.get("company_id")
            )
            return BlockService(
                user_id=user_id, company_id=company_id
            ).delete_block(block_id)
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


@schedule_ns.route("/slots")
class SlotsScheduleResource(Resource):

    @schedule_ns.doc(description="List Slots Schedule")
    @schedule_ns.expect(payload_slots_schedules, validate=True)
    @cross_origin()
    def post(self):
        """List Slots Schedule"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            company_id = request.headers.get(
                "company_id", request.environ.get("company_id")
            )
            return SlotsService(
                user_id=user_id, company_id=company_id
            ).list_slot(request.get_json())
        except Exception:
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "traceback": traceback.format_exc(),
                }
            )
