import traceback

from flask import jsonify, request
from flask_cors import cross_origin
from flask_restx import Namespace, Resource, fields, reqparse

from src.resource.commons.pagination import PaginationArguments
from src.service.company import CompanyService


pagination_arguments = reqparse.RequestParser()
PaginationArguments.add_to_parser(pagination_arguments)

companies_ns = Namespace("companies", description="Manager companies")


payload_add_companies = companies_ns.model(
    "PayloadAddCompany",
    {
        "name": fields.String(required=True, example="Company name", max_length=120),
        "email": fields.String(required=True, example="Company email", max_length=120),
        "phone_number": fields.String(required=True, example="Company phone number", max_length=40),
        "color": fields.String(required=False, example="Company color", max_length=20),
        "slug": fields.String(required=True, example="company-slug", max_length=120),
        "owner_id": fields.Integer(required=True, example=1),
    },
)

payload_update_companies = companies_ns.model(
    "PayloadUpdateCompany",
    {
        "name": fields.String(required=False, example="Company name", max_length=120),
        "email": fields.String(required=False, example="Company email", max_length=120),
        "phone_number": fields.String(
            required=False, example="Company phone number", max_length=40
        ),
        "color": fields.String(required=False, example="Company color", max_length=20),
        "slug": fields.String(required=False, example="company-slug", max_length=120),
        "owner_id": fields.Integer(required=False, example=1),
    },
)


@companies_ns.route("")
class CompanyResource(Resource):
    @companies_ns.doc(description="List Companies")
    @companies_ns.expect(pagination_arguments, validate=True)
    @cross_origin()
    def get(self):
        """List companies"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return CompanyService(user_id=user_id).list_companies(request.args.to_dict())
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

    @companies_ns.doc(description="Add companies")
    @companies_ns.expect(payload_add_companies, validate=True)
    @cross_origin()
    def post(self):
        """Add companies"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return CompanyService(user_id=user_id).add_company(request.get_json())
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


@companies_ns.route("/<int:company_id>")
class CompanyResourceManagerId(Resource):

    @companies_ns.doc(description="Update company by ID")
    @companies_ns.expect(payload_update_companies, validate=True)
    @cross_origin()
    def put(self, company_id: int):
        """Update owner by ID"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return CompanyService(user_id=user_id).update_company(company_id, request.get_json())
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

    @companies_ns.doc(description="Delete company by ID")
    @cross_origin()
    def delete(self, company_id: int):
        """Delete owner by ID"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return CompanyService(user_id=user_id).delete_company(company_id)
        except Exception as e:
            print("Coletando o error:", e)
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
