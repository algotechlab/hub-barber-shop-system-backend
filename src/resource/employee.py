import traceback

from flask import jsonify, request
from flask_cors import cross_origin
from flask_restx import Namespace, Resource, fields, reqparse

from src.resource.commons.pagination import PaginationArguments
from src.service.employee import EmployeeService

pagination_arguments = reqparse.RequestParser()
PaginationArguments.add_to_parser(pagination_arguments)

employee_ns = Namespace("employees", description="Manager employees")


payload_add_employees = employee_ns.model(
    "PayloadAddEmployee",
    {
        "first_name": fields.String(required=True, example="Employee name", max_length=120),
        "last_name": fields.String(required=True, example="Employee last name", max_length=120),
        "phone_number": fields.String(
            required=True, example="Employee phone number", max_length=40
        ),
    },
)

payload_update_employees = employee_ns.model(
    "PayloadUpdateEmployee",
    {
        "first_name": fields.String(required=False, example="Employee name", max_length=120),
        "last_name": fields.String(required=False, example="Employee last name", max_length=120),
        "phone_number": fields.String(
            required=False, example="Employee phone number", max_length=40
        ),
    },
)


@employee_ns.route("")
class EmployeeResource(Resource):
    @employee_ns.doc(description="List Employees")
    @employee_ns.expect(pagination_arguments, validate=True)
    @cross_origin()
    def get(self):
        """List Employees"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return EmployeeService(user_id=user_id).list_employees(request.args.to_dict())
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

    @employee_ns.doc(description="Add Employee")
    @employee_ns.expect(payload_add_employees, validate=True)
    @cross_origin()
    def post(self):
        """Add Employee"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return EmployeeService(user_id=user_id).add_employee(request.get_json())
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
