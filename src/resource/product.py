import traceback

from flask import jsonify, request
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource, fields, reqparse

from src.resource.commons.pagination import PaginationArguments
from src.service.product import ProductService
from src.service.product_employee import ProductEmployeeService


pagination_arguments = reqparse.RequestParser()
PaginationArguments.add_to_parser(pagination_arguments)

product_ns = Namespace("product", description="Manager product")


payload_add_product = product_ns.model(
    "PayloadAddProduct",
    {
        "description": fields.String(
            required=True, example="Corte de cabelo masculino", max_length=120
        ),
        "value_operation": fields.Float(
            required=True, example=50.00, description="Valor da operação"
        ),
        "time_to_spend": fields.String(
            required=True,
            example="00:30:00",
            description="Tempo estimado no formato HH:MM:SS",
        ),
        "commission": fields.Float(
            required=True,
            example=5.00,
            description="Comissão do colaborador sobre o serviço",
        ),
        "category": fields.String(
            required=True, example="Cabelo", max_length=30
        ),
    },
)

payload_update_product = product_ns.model(
    "PayloadUpdateProduct",
    {
        "description": fields.String(
            required=False, example="Corte de cabelo feminino", max_length=120
        ),
        "value_operation": fields.Float(required=False, example=60.00),
        "time_to_spend": fields.String(required=False, example="00:45:00"),
        "commission": fields.Float(required=False, example=7.00),
        "category": fields.String(
            required=False, example="Cabelo", max_length=30
        ),
    },
)

payload_add_product_employee = product_ns.model(
    "PayloadAddProductEmployee",
    {
        "product_id": fields.Integer(
            required=True, example=1, description="ID do produto"
        ),
        "employee_id": fields.Integer(
            required=True, example=10, description="ID do colaborador"
        ),
        "is_check": fields.Boolean(
            required=False,
            example=False,
            description="Marca colaborador está habilitado para o produto",
        ),
    },
)


@product_ns.route("")
class ProductResource(Resource):

    @product_ns.doc(description="List Products")
    @product_ns.expect(pagination_arguments, validate=True)
    @jwt_required()
    @cross_origin()
    def get(self):
        """List Products"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            company_id = request.headers.get(
                "company_id", request.environ.get("company_id")
            )
            return ProductService(
                user_id=user_id, company_id=company_id
            ).list_products(request.args.to_dict())
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

    @product_ns.doc(description="Add Employee")
    @product_ns.expect(payload_add_product, validate=True)
    @jwt_required()
    @cross_origin()
    def post(self):
        """Add Employee"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            company_id = request.headers.get(
                "company_id", request.environ.get("company_id")
            )
            return ProductService(
                user_id=user_id, company_id=company_id
            ).add_product(request.get_json())
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


@product_ns.route("/<int:product_id>")
class ProductManageIdResource(Resource):

    @product_ns.doc(description="Get product by ID")
    @jwt_required()
    @cross_origin()
    def get(self, product_id: int):
        """Get product by ID"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            company_id = request.headers.get(
                "company_id", request.environ.get("company_id")
            )
            return ProductService(
                user_id=user_id, company_id=company_id
            ).get_product(product_id)
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

    @product_ns.doc(description="Update product by ID")
    @product_ns.expect(payload_update_product, validate=True)
    @jwt_required()
    @cross_origin()
    def put(self, product_id: int):
        """Update product by ID"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            company_id = request.headers.get(
                "company_id", request.environ.get("company_id")
            )
            return ProductService(
                user_id=user_id, company_id=company_id
            ).update_product(product_id, request.get_json())
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

    @product_ns.doc(description="Delete product by ID")
    @jwt_required()
    @cross_origin()
    def delete(self, product_id: int):
        """Delete product by ID"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            company_id = request.headers.get(
                "company_id", request.environ.get("company_id")
            )
            return ProductService(
                user_id=user_id, company_id=company_id
            ).delete_product(product_id)
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


@product_ns.route("/employee")
class ProductEmployeResource(Resource):

    @product_ns.doc(description="Add Relation Product of Employee")
    @product_ns.expect(payload_add_product_employee, validate=True)
    @jwt_required()
    @cross_origin()
    def post(self):
        """Add Relation Product of Employee"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            company_id = request.headers.get(
                "company_id", request.environ.get("company_id")
            )
            return ProductEmployeeService(
                user_id=user_id, company_id=company_id
            ).add_product_employee(request.get_json())
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


@product_ns.route("/<int:product_id>/<int:employee_id>")
class ProductEmployeManageIdResource(Resource):

    @product_ns.doc(description="Delete product relation of employee by ID")
    @jwt_required()
    @cross_origin()
    def delete(self, product_id: int, employee_id: int):
        """Delete product relation of employee by ID"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            company_id = request.headers.get(
                "company_id", request.environ.get("company_id")
            )
            return ProductEmployeeService(
                user_id=user_id, company_id=company_id
            ).delete_product_employee(product_id, employee_id)
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
