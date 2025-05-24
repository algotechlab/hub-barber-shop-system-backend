# src/resource/shedule.py

import traceback

from flask import jsonify, request
from flask_cors import cross_origin
from flask_restx import Namespace, Resource, fields, reqparse

from src.core.shedule import SheduleCore

pagination_arguments_products = reqparse.RequestParser()
pagination_arguments_products.add_argument(
    "current_page", help="Current Page", default=1, type=int, required=False
)
pagination_arguments_products.add_argument(
    "rows_per_page", help="Rows per Page", default=10, type=int, required=False
)
pagination_arguments_products.add_argument(
    "order_by", help="Order By", default="", type=str, required=False
)
pagination_arguments_products.add_argument(
    "sort_by", help="Sort By", default="", type=str, required=False
)
pagination_arguments_products.add_argument(
    "filter_by", help="Filter By", default="", type=str, required=False
)


shedule_ns = Namespace("shedule", description="Manager shedule")


payload_add_shedule = shedule_ns.model(
    "SheduleAddPayload",
    {
        "product_id": fields.Integer(required=True, description="Product id"),
        "employee_id": fields.Integer(
            required=True, description="Employee id"
        ),
        "user_id": fields.Integer(required=True, description="User id"),
        "time_register": fields.DateTime(
            required=True, description="Time register time spent in HH:MM:SS"
        ),
    },
)


payload_update_shedule = shedule_ns.model(
    "SheduleUpdatePayload",
    {
        "product_id": fields.Integer(required=False, description="Product id"),
        "employee_id": fields.Integer(
            required=False, description="Employee id"
        ),
        "time_register": fields.DateTime(
            required=False, description="Time register time spent in HH:MM:SS"
        ),
    },
)


@shedule_ns.route("")
class SheduleManageResource(Resource):
    @shedule_ns.doc(description="Add shedule")
    @shedule_ns.expect(payload_add_shedule, validate=True)
    @cross_origin()
    def post(self):
        """Add shedule"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return SheduleCore(user_id=user_id).add_shedule(
                data=request.get_json()
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

    @shedule_ns.doc(description="List shedule")
    @shedule_ns.expect(pagination_arguments_products, validate=True)
    @cross_origin()
    def get(self):
        """List shedule"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return SheduleCore(user_id=user_id).list_shedule(
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


@shedule_ns.route("/<int:id>")
class SheduleManagerResourceId(Resource):
    @shedule_ns.doc(description="Update shedule")
    @shedule_ns.expect(payload_update_shedule, validate=True)
    @cross_origin()
    def put(self, id: int):
        """Update Shedule"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return SheduleCore(user_id=user_id).update_shedule(
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

    @shedule_ns.doc(description="Delete shedule")
    @cross_origin()
    def delete(self, id: int):
        """Delete shedule"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return SheduleCore(user_id=user_id).delete_shedule(
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
