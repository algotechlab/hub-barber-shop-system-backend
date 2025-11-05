# src/core/dashboard.py

import traceback

from flask import jsonify
from sqlalchemy import func, or_, select

from src.db.database import db
from src.model.model import BoxAccounting, Employee, IndicatedUsers, Invoice, Products
from src.utils.log import logdb
from src.utils.metadata import Metadata
from src.utils.pagination import Pagination


class DashBoardCore:
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.employee = Employee
        self.schedule = None  # TODO refatorar
        self.products = Products
        self.indicator_users = IndicatedUsers
        self.box_accounting = BoxAccounting
        self.invoice = Invoice

    def list_employees_ranking_paid(self, data: dict):
        try:
            pagination = Pagination(data)
            pagination_params, error = pagination.validate_params()
            if error:
                return jsonify(
                    {
                        "status_code": 400,
                        "message_id": "invalid_pagination_params",
                        "error": True,
                    }
                )

            stmt = (
                select(
                    self.employee.id,
                    self.employee.username,
                    func.count(self.schedule.is_check).label("total_paid"),
                )
                .join(
                    self.schedule,
                    self.schedule.employee_id == self.employee.id,
                )
                .where(
                    self.employee.is_deleted == False,
                    self.schedule.is_deleted == False,
                    self.schedule.is_check == True,
                )
                .group_by(
                    self.employee.id,
                    self.employee.username,
                )
            )

            if pagination_params.filter_by:
                filter_value = f"%{pagination_params.filter_by}%"
                try:
                    stmt = stmt.where(
                        or_(
                            func.unaccent(self.employee.username).ilike(
                                func.unaccent(filter_value)
                            ),
                        )
                    )
                except Exception:
                    stmt = stmt.filter(self.employee.username.ilike(filter_value))

            total_count = db.session.execute(
                select(func.count()).select_from(stmt.subquery())
            ).scalar()

            paginated_stmt = stmt.offset(
                (pagination_params.current_page - 1) * pagination_params.rows_per_page
            ).limit(pagination_params.rows_per_page)

            result = db.session.execute(paginated_stmt).fetchall()

            if not result:
                return (
                    jsonify(
                        {
                            "status_code": 404,
                            "message_id": "employees_ranking_paid_not_found",
                        }
                    ),
                    404,
                )

            metadata = pagination.build_metadata(total_count, pagination_params)
            return (
                jsonify(
                    {
                        "status_code": 200,
                        "data": Metadata(result).model_to_list(),
                        "message_id": "success_list_employees_ranking_paid",
                        "error": False,
                        "metadata": metadata,
                    }
                ),
                200,
            )

        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error in list employees ranking paid: \
                {str(e)}\n{traceback.format_exc()}",
            )
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "internal_server_error",
                        "error": str(e),
                    }
                ),
                500,
            )

    def most_approved_orders(self):
        try:
            stmt = (
                select(
                    self.products.id,
                    self.employee.username,
                    self.products.value_operation,
                    self.products.description,
                )
                .join(
                    self.schedule,
                    self.schedule.product_id == self.products.id,
                )
                .join(
                    self.employee,
                    self.schedule.employee_id == self.employee.id,
                )
                .where(
                    self.schedule.is_check == True,
                )
                .order_by(self.schedule.time_register.desc())
            )

            result = db.session.execute(stmt).fetchall()

            if not result:
                return (
                    jsonify(
                        {
                            "status_code": 404,
                            "message_id": "most_approved_orders_not_found",
                        }
                    ),
                    404,
                )

            return (
                jsonify(
                    {
                        "status_code": 200,
                        "data": Metadata(result).model_to_list(),
                        "message_id": "success_most_approved_orders",
                        "error": False,
                    }
                ),
                200,
            )

        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error in most approved orders: \
                {str(e)}\n{traceback.format_exc()}",
            )
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "internal_server_error",
                        "error": str(e),
                    }
                ),
                500,
            )

    def list_indicator_users(self):
        try:
            stmt = (
                select(
                    self.employee.username,
                    func.count(self.indicator_users.user_id).label("total_indication"),
                )
                .join(
                    self.indicator_users,
                    self.indicator_users.employee_id == self.employee.id,
                )
                .where(self.employee.is_deleted == False)
                .group_by(self.employee.username)
                .order_by(func.count(self.indicator_users.user_id).desc())
            )

            result = db.session.execute(stmt).fetchall()

            if not result:
                return jsonify(
                    {
                        "status_code": 404,
                        "message_id": "indicator_users_not_found",
                    }
                )

            return (
                jsonify(
                    {
                        "status_code": 200,
                        "data": Metadata(result).model_to_list(),
                        "message_id": "success_list_indicator_users",
                        "error": False,
                    }
                ),
                200,
            )

        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error in indicator users: \
                {str(e)}\n{traceback.format_exc()}",
            )
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "internal_server_error",
                        "error": str(e),
                    }
                ),
                500,
            )

    def summary_indicators(self):
        try:
            stmt = (
                select(
                    func.sum(
                        self.products.value_operation
                        + self.box_accounting.value_operation
                        + self.box_accounting.tip
                    ).label("total_paid"),
                    func.count(self.indicator_users.user_id).label(
                        "total_service_users"
                    ),
                    func.count(self.box_accounting.invoice_id).label("aprove_service"),
                )
                .select_from(self.invoice)
                .join(
                    self.box_accounting,
                    self.box_accounting.invoice_id == self.invoice.id,
                )
                .join(
                    self.schedule,
                    self.schedule.id == self.invoice.schedule_id,
                )
                .join(
                    self.products,
                    self.products.id == self.schedule.product_id,
                )
                .where(
                    self.schedule.is_check == True,
                    self.products.is_deleted == False,
                )
            )

            result = db.session.execute(stmt).fetchall()

            if not result:
                return jsonify(
                    {
                        "status_code": 404,
                        "message_id": "indicator_users_not_found",
                    }
                )

            return jsonify(
                {
                    "status_code": 200,
                    "data": Metadata(result).model_to_list(),
                    "message_id": "success_summary_indicators",
                    "error": False,
                }
            )

        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error in indicator users: \
                {str(e)}\n{traceback.format_exc()}",
            )
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "internal_server_error",
                        "error": str(e),
                    }
                ),
                500,
            )
