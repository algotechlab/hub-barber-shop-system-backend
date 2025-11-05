import traceback

from flask import jsonify, request
from flask_cors import cross_origin
from flask_restx import Namespace, Resource, fields

from src.core.login import LoginCore

login_ns = Namespace("login", description="Manager Login")


class PayloadFactoryLogin:
    @staticmethod
    def login_platform_payload(api):
        return api.model(
            "Login",
            {
                "phone": fields.String(example="61994261245", required=True),
            },
        )

    @staticmethod
    def login_platform_payload_employee(api):
        return api.model(
            "LoginEmployee",
            {
                "phone": fields.String(example="5569999999", required=True),
                "password": fields.String(example="********", required="True"),
            },
        )

    @staticmethod
    def reset_login_paylaod(api):
        return api.model(
            "LoginRest",
            {
                "email": fields.String(example="", required=True),
                "password": fields.String(example="********", required="True"),
            },
        )

    @staticmethod
    def reset_master_password(api):
        return api.model(
            "ResetMasterPassword",
            {"id": fields.Integer(example=3, required=True)},
        )


login_payload = PayloadFactoryLogin.login_platform_payload(login_ns)
login_payload_employee = PayloadFactoryLogin.login_platform_payload_employee(login_ns)
rest_password_payload = PayloadFactoryLogin.reset_login_paylaod(login_ns)
rest_password_master_payload = PayloadFactoryLogin.reset_master_password(login_ns)


@login_ns.route("")
class LoginResource(Resource):
    @login_ns.doc(description="Get User Login")
    @login_ns.expect(login_payload, validate=True)
    @cross_origin()
    def post(self):
        """Get user login"""
        try:
            return LoginCore().get_login(request.get_json())
        except Exception as e:
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "error": True,
                    "exception": str(e),
                    "traceback": traceback.format_exc(),
                }
            )


@login_ns.route("/employee")
class ResourceLoginManagerEmployee(Resource):
    @login_ns.doc(description="Get User Login Employee")
    @login_ns.expect(login_payload_employee, validate=True)
    @cross_origin()
    def post(self):
        """Get user login Employee"""
        try:
            return LoginCore().get_login_employee(data=request.get_json())
        except Exception as e:
            print("Errro coletado com sucesso", e)
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "error": True,
                    "exception": str(e),
                    "traceback": traceback.format_exc(),
                }
            )


@login_ns.route("/reset-master")
class ResetPasswordResourceMaster(Resource):
    # @jwt_required()
    @login_ns.doc(description="Reset Password Master")
    @login_ns.expect(rest_password_master_payload, validate=True)
    @cross_origin()
    def post(self):
        """Request resert password master"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))

            return LoginCore(user_id=user_id).reset_password_authorization(
                data=request.get_json()
            )
        except Exception as e:
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "error": True,
                    "exception": str(e),
                    "traceback": traceback.format_exc(),
                }
            )
