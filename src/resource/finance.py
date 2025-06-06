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
