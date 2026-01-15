import traceback

from flask import jsonify, request
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource, fields, reqparse

from src.resource.commons.pagination import PaginationArguments
from src.service.owner import OwnerService


pagination_arguments = reqparse.RequestParser()
PaginationArguments.add_to_parser(pagination_arguments)

owner_ns = Namespace("owners", description="Manager owners")


payload_add_owners = owner_ns.model(
    "PayloadAddOwner",
    {
        "first_name": fields.String(
            required=True, example="Owner name", max_length=120
        ),
        "last_name": fields.String(
            required=True, example="Owner last name", max_length=120
        ),
        "email": fields.String(
            required=True, example="Owner email", max_length=120
        ),
        "phone_number": fields.String(
            required=True, example="Owner phone number", max_length=40
        ),
        "hashed_password": fields.String(
            required=True, example="Owner password", max_length=300
        ),
    },
)

payload_update_owners = owner_ns.model(
    "PayloadUpdateOwner",
    {
        "first_name": fields.String(
            required=False, example="Owner name", max_length=120
        ),
        "last_name": fields.String(
            required=False, example="Owner last name", max_length=120
        ),
        "email": fields.String(
            required=False, example="Owner email", max_length=120
        ),
        "phone_number": fields.String(
            required=False, example="Owner phone number", max_length=40
        ),
    },
)


@owner_ns.route("")
class OwnerResource(Resource):
    @owner_ns.doc(description="List Owners")
    @owner_ns.expect(pagination_arguments, validate=True)
    # @jwt_required()
    @cross_origin()
    def get(self):
        """List owners"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return OwnerService(user_id=user_id).list_owners(
                request.args.to_dict()
            )
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

    @owner_ns.doc(description="Add owners")
    @owner_ns.expect(payload_add_owners, validate=True)
    # @jwt_required()
    @cross_origin()
    def post(self):
        """Add owners"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return OwnerService(user_id=user_id).add_owner(request.get_json())
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


@owner_ns.route("/<int:owner_id>")
class OwnerResourceManagerId(Resource):
    @owner_ns.doc(description="Get owner by ID")
    # @jwt_required()
    @cross_origin()
    def get(self, owner_id: int):
        """Get owner by ID"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return OwnerService(user_id=user_id).get_owner(owner_id)
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

    @owner_ns.doc(description="Update owner by ID")
    @owner_ns.expect(payload_update_owners, validate=True)
    # @jwt_required()
    @cross_origin()
    def put(self, owner_id: int):
        """Update owner by ID"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return OwnerService(user_id=user_id).update_owner(
                owner_id, request.get_json()
            )
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

    @owner_ns.doc(description="Delete owner by ID")
    # @jwt_required()
    @cross_origin()
    def delete(self, owner_id: int):
        """Delete owner by ID"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return OwnerService(user_id=user_id).delete_owner(owner_id)
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
