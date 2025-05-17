# src/resource/employee
import traceback

from flask import jsonify, request
from flask_cors import cross_origin
from flask_restx import Namespace, Resource, fields, reqparse

from src.core.employee import EmployeeCore

pagination_arguments_employees = reqparse.RequestParser()
pagination_arguments_employees.add_argument(
    "current_page", help="Current Page", default=1, type=int, required=False
)
pagination_arguments_employees.add_argument(
    "rows_per_page", help="Rows per Page", default=10, type=int, required=False
)
pagination_arguments_employees.add_argument(
    "order_by", help="Order By", default="", type=str, required=False
)
pagination_arguments_employees.add_argument(
    "sort_by", help="Sort By", default="", type=str, required=False
)
pagination_arguments_employees.add_argument(
    "filter_by", help="Filter By", default="", type=str, required=False
)
pagination_arguments_employees.add_argument(
    "filter_value", help="Filter Value", default="", type=str, required=False
)


employee_ns = Namespace("employee", description="Manager Employee")

payload_add_employees = employee_ns.model(
    "PayloadAddEmployees",
    {
        "username": fields.String(
            required=True, example="User name", max_length=120
        ),
        "cpf": fields.String(required=True, example="Cpf", max_length=20),
        "rg": fields.String(required=True, example="rg", max_length=20),
        "date_of_birth": fields.DateTime(
            dt_format="%Y-%m-%d",
            description="The person's birth date in %Y-%m-%d format",
        ),
        "nickname": fields.String(
            required=True, example="Nickname", max_length=300
        ),
        "email": fields.String(required=True, example="Email", max_length=300),
        "phone": fields.String(required=True, example="Phone", max_length=40),
        "password": fields.String(
            required=True, example="Password", max_length=300
        ),
    },
)

payload_update_employees = employee_ns.model(
    "PayloadUpdateEmployees",
    {
        "username": fields.String(
            required=False, example="User name", max_length=120
        ),
        "cpf": fields.String(required=False, example="Cpf", max_length=20),
        "rg": fields.String(required=False, example="rg", max_length=20),
        "date_of_birth": fields.DateTime(
            dt_format="iso8601",
            description="The person's birth date in ISO 8601 format",
        ),
        "nickname": fields.String(
            required=False, example="Nickname", max_length=300
        ),
        "email": fields.String(
            required=False, example="Email", max_length=300
        ),
        "phone": fields.String(required=False, example="Phone", max_length=40),
        "password": fields.String(
            required=False, example="Password", max_length=300
        ),
    },
)


@employee_ns.route("")
class EmployeeResourceManager(Resource):
    @employee_ns.doc(description="List Employees")
    @employee_ns.expect(pagination_arguments_employees, validate=True)
    @cross_origin()
    def get(self):
        """List employees"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return EmployeeCore(user_id=user_id).list_employees(
                request.args.to_dict()
            )
        except Exception:
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "traceback": traceback.format_exc(),
                }
            )

    @employee_ns.doc(description="Add Employees")
    @employee_ns.expect(payload_add_employees, validate=True)
    @cross_origin()
    def post(self):
        """Add employees"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return EmployeeCore(user_id=user_id).add_employee(
                request.get_json()
            )
        except Exception:
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "traceback": traceback.format_exc(),
                }
            )


@employee_ns.route("/<int:id>")
class EmployeeResourceManagerId(Resource):
    @employee_ns.doc(description="Get Employee")
    @cross_origin()
    def get(self, id: int):
        """Get id"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return EmployeeCore(user_id=user_id).get_employee(id)
        except Exception:
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "traceback": traceback.format_exc(),
                }
            )

    @employee_ns.doc(description="Update Employees")
    @employee_ns.expect(payload_update_employees, validate=True)
    @cross_origin()
    def put(self, id: int):
        """Update employees"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return EmployeeCore(user_id=user_id).update_employee(
                id, request.get_json()
            )
        except Exception:
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "traceback": traceback.format_exc(),
                }
            )

    @employee_ns.doc(description="Delete Employee")
    @cross_origin()
    def delete(self, id: int):
        """Delete employees"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return EmployeeCore(user_id=user_id).delete_employee(id)
        except Exception:
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "traceback": traceback.format_exc(),
                }
            )
