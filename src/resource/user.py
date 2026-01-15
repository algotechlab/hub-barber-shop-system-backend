import traceback

from flask import jsonify, request
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource, fields, reqparse

from src.resource.commons.pagination import PaginationArguments
from src.service.user import UserService


pagination_arguments = reqparse.RequestParser()
PaginationArguments.add_to_parser(pagination_arguments)

user_us = Namespace("users", description="Manager users")

payload_add_users = user_us.model(
    "PayloadAddUser",
    {
        "username": fields.String(
            required=True, example="User name", max_length=120
        ),
        "phone": fields.String(
            required=True, example="User phone", max_length=40
        ),
        "email": fields.String(
            required=False, example="User email", max_length=120
        ),
        "password": fields.String(
            required=True, example="User password", max_length=300
        ),
        "company_id": fields.Integer(required=True, example=4),
    },
)

payload_update_users = user_us.model(
    "PayloadUpdateUser",
    {
        "username": fields.String(
            required=False, example="User name", max_length=120
        ),
        "phone": fields.String(
            required=True, example="User phone", max_length=40
        ),
        "email": fields.String(
            required=False, example="User email", max_length=120
        ),
        "password": fields.String(
            required=False, example="User password", max_length=300
        ),
    },
)


@user_us.route("")
class UserResource(Resource):
    @user_us.doc(description="List Users")
    @user_us.expect(pagination_arguments, validate=True)
    # @jwt_required()
    @cross_origin()
    def get(self):
        """List users"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            company_id = request.headers.get(
                "company_id", request.environ.get("company_id")
            )
            return UserService(
                user_id=user_id, company_id=company_id
            ).list_users(request.args.to_dict())
        except Exception:
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "traceback": traceback.format_exc(),
                }
            )

    @user_us.doc(description="Add users")
    @user_us.expect(payload_add_users, validate=True)
    # @jwt_required()
    @cross_origin()
    def post(self):
        """Add users"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            company_id = request.headers.get(
                "company_id", request.environ.get("company_id")
            )
            return UserService(
                user_id=user_id, company_id=company_id
            ).add_user(request.get_json())
        except Exception:
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "traceback": traceback.format_exc(),
                }
            )


@user_us.route("/<int:id>")
class UserResourcerId(Resource):
    @user_us.doc(description="Get User")
    # @jwt_required()
    @cross_origin()
    def get(self, id: int):
        """Get id"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            company_id = request.headers.get(
                "company_id", request.environ.get("company_id")
            )
            return UserService(
                user_id=user_id, company_id=company_id
            ).get_user(id=id)
        except Exception:
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "traceback": traceback.format_exc(),
                }
            )

    @user_us.doc(description="Update User")
    @user_us.expect(payload_update_users, validate=True)
    # @jwt_required()
    @cross_origin()
    def put(self, id: int):
        """Update users"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            company_id = request.headers.get(
                "company_id", request.environ.get("company_id")
            )
            return UserService(
                user_id=user_id, company_id=company_id
            ).update_user(id=id, data=request.get_json())
        except Exception:
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "traceback": traceback.format_exc(),
                }
            )

    @user_us.doc(description="Delete User")
    # @jwt_required()
    @cross_origin()
    def delete(self, id: int):
        """Delete users"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            company_id = request.headers.get(
                "company_id", request.environ.get("company_id")
            )
            return UserService(user_id=user_id, company_id=company_id).delete(
                id=id
            )
        except Exception:
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "traceback": traceback.format_exc(),
                }
            )
