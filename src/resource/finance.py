# src/resource/finance.py

import traceback

from flask import jsonify, request
from flask_cors import cross_origin
from flask_restx import Namespace, Resource

from src.core.finance import FinanceCore

finance_ns = Namespace("finance", description="Manager finance")


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
    @cross_origin()
    def get(self):
        """List OutPut Exit Payments"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return FinanceCore(user_id=user_id).list_out_put_exit_payments()
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
