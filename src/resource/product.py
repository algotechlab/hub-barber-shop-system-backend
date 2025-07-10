# src/resource/product.py

import traceback

from flask import jsonify, request
from flask_cors import cross_origin
from flask_restx import Namespace, Resource, fields, reqparse
from werkzeug.datastructures import FileStorage

from src.core.product import ProductCore

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


product_ns = Namespace("product", description="Manager products")


payload_add_products = product_ns.model(
    "Product",
    {
        "description": fields.String(
            required=True, description="Product description"
        ),
        "value_operation": fields.Float(
            required=True, description="Operation value"
        ),
        "time_to_spend": fields.String(
            required=True, description="Time spent in HH:MM:SS"
        ),
        "commission": fields.Float(
            required=True,
            description="Commission percentage (e.g., 50.0 for 50%)",
        ),
        "category": fields.String(
            required=True, description="Product category"
        ),
    },
)

payload_update_products = product_ns.model(
    "Product",
    {
        "description": fields.String(
            required=False, description="Product description"
        ),
        "value_operation": fields.Float(
            required=False, description="Operation value"
        ),
        "time_to_spend": fields.String(
            required=False, description="Time spent in HH:MM:SS"
        ),
        "commission": fields.Float(
            required=False,
            description="Commission percentage (e.g., 50.0 for 50%)",
        ),
        "category": fields.String(
            required=False, description="Product category"
        ),
    },
)

paylaod_add_associate_employee = product_ns.model(
    "PayloadAddAssociateEmployee",
    {
        "employee_id": fields.Integer(
            required=True, description="Employee ID", example=1
        ), 
        "product_id": fields.Integer(
            required=True, description="Product ID", example=1
        )
    }
)

payload_parser = reqparse.RequestParser()
payload_parser.add_argument(
    "description",
    type=str,
    required=True,
    help="Product description",
    location="form",
)
payload_parser.add_argument(
    "value_operation",
    type=float,
    required=True,
    help="Operation value",
    location="form",
)
payload_parser.add_argument(
    "time_to_spend",
    type=str,
    required=True,
    help="Time spent in HH:MM:SS",
    location="form",
)
payload_parser.add_argument(
    "commission",
    type=float,
    required=True,
    help="Commission percentage",
    location="form",
)
payload_parser.add_argument(
    "category",
    type=str,
    required=True,
    help="Product category",
    location="form",
)
payload_parser.add_argument(
    "image",
    type=FileStorage,
    required=False,
    help="Upload an image (PNG or JPEG)",
    location="files",
)


@product_ns.route("")
class ProductManagerResource(Resource):
    @product_ns.doc(description="Add products")
    @product_ns.expect(payload_parser, validate=True)
    @cross_origin()
    def post(self):
        """Add products"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            args = payload_parser.parse_args()
            data = {
                "description": args["description"],
                "value_operation": args["value_operation"],
                "time_to_spend": args["time_to_spend"],
                "commission": args["commission"],
                "category": args["category"],
            }
            image_file = args["image"]
            return ProductCore(user_id=user_id).add_product(
                data=data, image_file=image_file
            )
        except Exception:
            return {
                "status_code": 500,
                "message_id": "something_went_wrong",
                "traceback": traceback.format_exc(),
                "error": True,
            }, 500

    @product_ns.doc(description="List produtc")
    @product_ns.expect(pagination_arguments_products, validate=True)
    @cross_origin()
    def get(self):
        """List products"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return ProductCore(user_id=user_id).list_products(
                request.args.to_dict()
            )
        except Exception:
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "something_went_wrong",
                        "error": True,
                    },
                )
            ), 500

@product_ns.route("/<int:id>")
class ProductManagerResourceId(Resource):
    @product_ns.doc(description="Update products")
    @product_ns.expect(payload_update_products, validate=True)
    @cross_origin()
    def put(self, id: int):
        """Update products"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return ProductCore(user_id=user_id).update_product(
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

    @product_ns.doc(description="Delete products")
    @cross_origin()
    def delete(self, id: int):
        """Delete products"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return ProductCore(user_id=user_id).delete_product(id=id)
        except Exception:
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "traceback": traceback.format_exc(),
                }
            )

@product_ns.route("/employees")
class ProductManangeAssociateEmployees(Resource):
    
    @product_ns.doc(description="Add products associate employees")
    @product_ns.expect(paylaod_add_associate_employee, validate=True)
    @cross_origin()
    def post(self):
        """Add products asscoaite employees"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return ProductCore(user_id=user_id).add_products_employees(
                data=request.get_json()
            )
        except Exception:
            return {
                "status_code": 500,
                "message_id": "something_went_wrong",
                "traceback": traceback.format_exc(),
                "error": True,
            }, 500

@product_ns.route("/employees/<int:id>")
class ProductManangeAssociateEmployeesId(Resource):
    @product_ns.doc(description="Delete products associate employees")
    @cross_origin()
    def delete(self, id: int):
        """Delete products associate employees"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return ProductCore(user_id=user_id).delete_product_associate_employee(id=id)
        except Exception:
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "traceback": traceback.format_exc(),
                }
            )