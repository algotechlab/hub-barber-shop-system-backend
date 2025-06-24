# src/resource/dashboard.py
import traceback

from flask import jsonify, request
from flask_cors import cross_origin
from flask_restx import Namespace, Resource, reqparse
from src.core.dashboard import DashBoardCore

pagination_arguments_dashboard = reqparse.RequestParser()
pagination_arguments_dashboard.add_argument(
    "current_page", help="Current Page", default=1, type=int, required=False
)
pagination_arguments_dashboard.add_argument(
    "rows_per_page", help="Rows per Page", default=10, type=int, required=False
)
pagination_arguments_dashboard.add_argument(
    "order_by", help="Order By", default="", type=str, required=False
)
pagination_arguments_dashboard.add_argument(
    "sort_by", help="Sort By", default="", type=str, required=False
)
pagination_arguments_dashboard.add_argument(
    "filter_by", help="Filter By", default="", type=str, required=False
)

dashboard_ns = Namespace("dashboard", description="Manager Dashboard")


@dashboard_ns.route("/list-ranking-paid-employees")
class ManagerDashboard(Resource):
    @dashboard_ns.doc(description="List ranking paid employees")
    @dashboard_ns.expect(pagination_arguments_dashboard, validate=True)
    @cross_origin()
    def get(self):
        """List ranking paid employees"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return DashBoardCore(user_id=user_id).list_employees_ranking_paid(
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


@dashboard_ns.route("/most-approved-orders")
class ManagaDashBoardApprovedOrders(Resource):
    @dashboard_ns.doc(description="List most approved orders")
    @cross_origin()
    def get(self):
        """List most approved orders"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return DashBoardCore(user_id=user_id).most_approved_orders()
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


@dashboard_ns.route("/list-ranking-indicator-users")
class ManageDashBoardListRankingIndicatorUsers(Resource):
    @dashboard_ns.doc(description="List ranking indicator uses")
    @cross_origin()
    def get(self):
        """List ranking indicator users"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return DashBoardCore(user_id=user_id).list_indicator_users()
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


@dashboard_ns.route("/summary-indicators")
class ManageDashBoardSummaryIndicators(Resource):
    @dashboard_ns.doc(description="List summary indicators")
    @cross_origin()
    def get(self):
        """List summary indicators"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return DashBoardCore(user_id=user_id).summary_indicators()
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
