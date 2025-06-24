# src/resource/dashboard.py

from flask_restx import Namespace, reqparse

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


dashboard_ns = Namespace("dashboard", description="Manager Dashboard")
