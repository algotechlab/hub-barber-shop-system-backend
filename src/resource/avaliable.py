# src/resource/avaliable
import traceback

from flask import jsonify, request
from flask_cors import cross_origin
from flask_restx import Namespace, Resource, fields, reqparse

from src.core.avaliable import AvaliableCore

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


avaliable_ns = Namespace("avaliable", description="Manager Avaliable")

payload_add_avaliable = avaliable_ns.model(
    "avaliableAddPayload",
    {
        "star": fields.Integer(required=True, description="Star"),
        "product_id": fields.Integer(required=True, description="Product id"),
        "employee_id": fields.Integer(required=True, description="Employee id"),
        "user_id": fields.Integer(required=True, description="User id"),
        "observer": fields.String(required=True, description="Observer"),
    },
)


@avaliable_ns.route("")
class ManageAvaliable(Resource):
    @avaliable_ns.doc(description="List Avaliable")
    @avaliable_ns.expect(pagination_arguments_employees, validate=True)
    @cross_origin()
    def get(self):
        """Get list avaliable users"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return AvaliableCore(user_id=user_id).list_avaliable(request.args.to_dict())
        except Exception:
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "traceback": traceback.format_exc(),
                }
            )

    @avaliable_ns.doc(description="Add Avaliable")
    @avaliable_ns.expect(payload_add_avaliable, validate=True)
    @cross_origin()
    def post(self):
        """Add  avaliable users"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return AvaliableCore(user_id=user_id).add_avaliable(request.get_json())
        except Exception:
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "traceback": traceback.format_exc(),
                }
            )


@avaliable_ns.route("/count-avaliable")
class ManageAvaliableId(Resource):
    @avaliable_ns.doc(description="Count Avaliable")
    @cross_origin()
    def get(self):
        """Count  avaliable users"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return AvaliableCore(user_id=user_id).count_start()
        except Exception:
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "traceback": traceback.format_exc(),
                }
            )
