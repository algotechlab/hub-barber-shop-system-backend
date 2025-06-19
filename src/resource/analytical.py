# src/resource/analytical.py
import traceback

from flask import jsonify, request
from flask_cors import cross_origin
from flask_restx import Namespace, Resource

from src.core.analytical import AnalyticalCore

analytical_ns = Namespace("analytical", description="Manager Analytical")


@analytical_ns.route("/summary-client/<int:id>")
class AnalyticalVisitisBarberShop(Resource):
    @analytical_ns.doc(description="Summary Client Barber Shop")
    @cross_origin()
    def get(self, id: int):
        """Summary Client Barber Shop"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return AnalyticalCore(user_id=user_id).summary_client(user_id=id)
        except Exception:
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "something_went_wrong",
                    "traceback": traceback.format_exc(),
                }
            )
