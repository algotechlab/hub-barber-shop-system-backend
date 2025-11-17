import traceback

from flask import jsonify, request
from flask_cors import cross_origin
from flask_restx import Namespace, Resource, fields

from src.service.login import LoginService


login_us = Namespace("login", description="Manager Login")


payload_login_users = login_us.model(
    "PayloadLoginUser",
    {
        "phone": fields.String(
            required=True, example="User phone", max_length=40
        ),
        "hashed_password": fields.String(
            required=True, example="User password", max_length=300
        ),
    },
)


payload_login_employee = login_us.model(
    "PayloadLoginEmployee",
    {
        "phone_number": fields.String(
            required=True, example="User phone", max_length=40
        ),
        "hashed_password": fields.String(
            required=True, example="User password", max_length=300
        ),
    },
)

payload_login_owner = login_us.model(
    "PayloadLoginEmployee",
    {
        "phone_number": fields.String(
            required=True, example="User phone", max_length=40
        ),
        "hashed_password": fields.String(
            required=True, example="User password", max_length=300
        ),
    },
)


@login_us.route("/login-user")
class LoginUserResource(Resource):
    @login_us.doc(description="Post login user")
    @login_us.expect(payload_login_users, validate=True)
    @cross_origin()
    def post(self):
        """Post login user"""
        try:
            return LoginService().login_user(request.get_json())
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


@login_us.route("/login-employee")
class LoginEmployeeResource(Resource):

    @login_us.doc(description="Post login employee")
    @login_us.expect(payload_login_employee, validate=True)
    @cross_origin()
    def post(self):
        """Post login emloyee"""
        try:
            return LoginService().login_employee(request.get_json())
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


@login_us.route("/login-owner")
class LoginOwnerResource(Resource):

    @login_us.doc(description="Post login owner")
    @login_us.expect(payload_login_employee, validate=True)
    @cross_origin()
    def post(self):
        """Post login owner"""
        try:
            return LoginService().login_owner(request.get_json())
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
