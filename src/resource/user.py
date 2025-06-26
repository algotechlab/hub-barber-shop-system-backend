# src/resource/user.py
import traceback

from flask import jsonify, request
from flask_cors import cross_origin
from flask_restx import Namespace, Resource, fields, reqparse

from src.core.user import UserCore

pagination_arguments_users = reqparse.RequestParser()
pagination_arguments_users.add_argument(
    "current_page", help="Current Page", default=1, type=int, required=False
)
pagination_arguments_users.add_argument(
    "rows_per_page", help="Rows per Page", default=10, type=int, required=False
)
pagination_arguments_users.add_argument(
    "order_by", help="Order By", default="", type=str, required=False
)
pagination_arguments_users.add_argument(
    "sort_by", help="Sort By", default="", type=str, required=False
)
pagination_arguments_users.add_argument(
    "filter_by", help="Filter By", default="", type=str, required=False
)
user_us = Namespace("user", description="Manager users")

payload_add_users = user_us.model(
    "PayloadAddUser",
    {
        "username": fields.String(
            required=True, example="User name", max_length=120
        ),
        "lastname": fields.String(
            required=True, example="User name", max_length=120
        ),
        "phone": fields.String(
            required=True, example="User phone", max_length=40
        ),
    },
)

payload_update_users = user_us.model(
    "PayloadUpdateUser",
    {
        "username": fields.String(
            required=False, example="User name", max_length=120
        ),
        "lastname": fields.String(
            required=False, example="User name", max_length=120
        ),
        "password": fields.String(
            required=False, example="User password", max_length=300
        ),
    },
)


@user_us.route("")
class UserResource(Resource):
    
    @user_us.doc(description="List Users")
    @user_us.expect(pagination_arguments_users, validate=True)
    @cross_origin()
    def get(self):
        """List users"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return UserCore(user_id=user_id).list_users(request.args.to_dict())
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
    @cross_origin()
    def post(self):
        """Add users"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return UserCore(user_id=user_id).add_user(request.get_json())
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
    @cross_origin()
    def get(self, id: int):
        """Get id"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return UserCore(user_id=user_id).get_user(id=id)
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
    @cross_origin()
    def put(self, id: int):
        """Update users"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return UserCore(user_id=user_id).update_user(
                id=id, data=request.get_json()
            )
        except Exception:
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "traceback": traceback.format_exc(),
                }
            )

    @user_us.doc(description="Delete User")
    @cross_origin()
    def delete(self, id: int):
        """Delete users"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return UserCore(user_id=user_id).delete(id=id)
        except Exception:
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "traceback": traceback.format_exc(),
                }
            )
