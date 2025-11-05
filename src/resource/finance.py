# src/resource/finance.py

import traceback

from flask import jsonify, request
from flask_cors import cross_origin
from flask_restx import Namespace, Resource, fields, reqparse

from src.core.finance import FinanceCore

pagination_arguments_finance = reqparse.RequestParser()
pagination_arguments_finance.add_argument(
    "current_page", help="Current Page", default=1, type=int, required=False
)
pagination_arguments_finance.add_argument(
    "rows_per_page", help="Rows per Page", default=10, type=int, required=False
)
pagination_arguments_finance.add_argument(
    "order_by", help="Order By", default="", type=str, required=False
)
pagination_arguments_finance.add_argument(
    "sort_by", help="Sort By", default="", type=str, required=False
)
pagination_arguments_finance.add_argument(
    "filter_by", help="Filter By", default="", type=str, required=False
)


finance_ns = Namespace("finance", description="Manager finance")


payload_update_finance = finance_ns.model(
    "PayloadUpdateFinance",
    {
        "payments_id": fields.Integer(
            required=False, example=1, description="Payments ID"
        ),
        "tips": fields.Float(required=False, description="Tip"),
        "value_operation": fields.Float(required=False, description="Operation value"),
    },
)

payload_add_finance = finance_ns.model(
    "PayloadAddOutPutFinance",
    {
        "value_operation": fields.Float(
            required=False, description="Operation value", example=0.0
        ),
        "description": fields.String(
            required=False, description="Description out put finance"
        ),
        "type_payments": fields.String(required=False, description="Type payments"),
    },
)

payload_update_out_put_finance = finance_ns.model(
    "PayloadUpdateOutPutFinance",
    {
        "value_operation": fields.Float(
            required=False, description="Operation value", example=0.0
        ),
        "description": fields.String(
            required=False, description="Description out put finance"
        ),
        "type_payments": fields.String(required=False, description="Type payments"),
    },
)


@finance_ns.route("/<int:id>")
class FinanceResourceManager(Resource):
    @finance_ns.doc(
        description="Update payments relashionship invoce and box accounting"
    )
    @finance_ns.expect(payload_update_finance, validate=True)
    @cross_origin()
    def put(self, id: int):
        """Update payments relashionship invoce and box accounting"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return FinanceCore(user_id=user_id).update_invoce_payments(
                invoce_id=id, data=request.get_json()
            )
        except Exception as e:
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "something_went_wrong",
                        "error": True,
                        "exception": str(e),
                        "traceback": traceback.format_exc(),
                    }
                ),
                500,
            )


@finance_ns.route("/types-payments")
class FinancePaymentsTypesResource(Resource):
    @finance_ns.doc(description="List type payments")
    @cross_origin()
    def get(self):
        """List type payments"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return FinanceCore(user_id=user_id).list_type_payments()
        except Exception as e:
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "something_went_wrong",
                        "error": True,
                        "exception": str(e),
                        "traceback": traceback.format_exc(),
                    }
                ),
                500,
            )


@finance_ns.route("/summary-payments")
class ListTypeSummaryPayments(Resource):
    @finance_ns.doc(description="List type summary payments")
    @cross_origin()
    def get(self):
        """List type summary payments"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return FinanceCore(user_id=user_id).list_summary_types_payments()
        except Exception as e:
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "something_went_wrong",
                        "error": True,
                        "exception": str(e),
                        "traceback": traceback.format_exc(),
                    }
                ),
                500,
            )


@finance_ns.route("/totals-payments")
class ListTotalsPayments(Resource):
    @finance_ns.doc(description="List totals payments")
    @cross_origin()
    def get(self):
        """List totals payments"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return FinanceCore(user_id=user_id).list_total_payments()
        except Exception as e:
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "something_went_wrong",
                        "error": True,
                        "exception": str(e),
                        "traceback": traceback.format_exc(),
                    }
                ),
                500,
            )


@finance_ns.route("/out-put-exit-payments")
class ListOutPutExitPayments(Resource):
    @finance_ns.doc(description="List OutPut Exit Payments")
    @finance_ns.expect(pagination_arguments_finance, valiedate=True)
    @cross_origin()
    def get(self):
        """List OutPut Exit Payments"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return FinanceCore(user_id=user_id).list_out_put_exit_payments(
                data=request.args.to_dict()
            )
        except Exception as e:
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "something_went_wrong",
                        "error": True,
                        "exception": str(e),
                        "traceback": traceback.format_exc(),
                    }
                ),
                500,
            )

    @finance_ns.doc(description="Add OutPut Exit Payments")
    @finance_ns.expect(payload_add_finance, validate=True)
    @cross_origin()
    def post(self):
        """Add OutPut Exit Payments"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return FinanceCore(user_id=user_id).add_out_put_finance(
                data=request.get_json()
            )
        except Exception as e:
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "something_went_wrong",
                        "error": True,
                        "exception": str(e),
                        "traceback": traceback.format_exc(),
                    }
                ),
                500,
            )


@finance_ns.route("/out-put-exit-payments/<int:id>")
class OutPutExitsPaymentsManaget(Resource):
    @finance_ns.doc(description="Get ID OutPut Exit Payments")
    @cross_origin()
    def get(self, id: int):
        """Get id OutPut Exit Payments"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return FinanceCore(user_id=user_id).get_out_put_finance(id=id)

        except Exception as e:
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "something_went_wrong",
                        "error": True,
                        "exception": str(e),
                        "traceback": traceback.format_exc(),
                    }
                ),
                500,
            )

    @finance_ns.doc(description="Update OutPut Exit Payments")
    @finance_ns.expect(payload_update_out_put_finance, validate=True)
    @cross_origin()
    def put(self, id: int):
        """Update OutPut Exit Payments"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return FinanceCore(user_id=user_id).update_out_put_finance(
                id=id, data=request.get_json()
            )

        except Exception as e:
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "something_went_wrong",
                        "error": True,
                        "exception": str(e),
                        "traceback": traceback.format_exc(),
                    }
                ),
                500,
            )


# list_invoice_payments
@finance_ns.route("/list-invoice-payments")
class ListInvoicePayments(Resource):
    @finance_ns.doc(description="List Invoice Payments")
    @finance_ns.expect(pagination_arguments_finance, validate=True)
    @cross_origin()
    def get(self):
        """List Invoice Payments"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return FinanceCore(user_id=user_id).list_invoice_payments(
                data=request.args.to_dict()
            )
        except Exception as e:
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "something_went_wrong",
                        "error": True,
                        "exception": str(e),
                        "traceback": traceback.format_exc(),
                    }
                ),
                500,
            )
