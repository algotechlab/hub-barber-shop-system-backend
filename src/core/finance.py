# src/core/finance.py

import traceback

from flask import jsonify
from sqlalchemy import func, insert, or_, select, update

from src.db.database import db
from src.model.model import (
    BoxAccounting,
    Employee,
    Invoice,
    InvoiceOutPut,
    Payments,
    Products,
    User,
)
from src.utils.log import logdb
from src.utils.metadata import Metadata
from src.utils.pagination import Pagination


class FinanceCore:
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.finance_payments = Payments
        self.invoice = Invoice
        self.box_accounting = BoxAccounting
        self.schedule = None  # TODO refatorar
        self.products = Products
        self.invoice_out_put = InvoiceOutPut
        self.user = User
        self.products = Products
        self.employees = Employee
        self.invoice_out_put = InvoiceOutPut

    def add_out_put_finance(self, data: dict):
        try:
            stmt = insert(self.invoice_out_put).values(
                description=data.get("description"),
                value_operation=data.get("value_operation"),
                types_payments=data.get("type_payments"),
            )

            db.session.execute(stmt)
            db.session.commit()

            return (
                jsonify(
                    {
                        "status_code": 200,
                        "message_id": "success_add_out_put_finance",
                        "error": False,
                    }
                ),
                200,
            )

        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error in add out put finance: \
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

    def get_out_put_finance(self, id: int):
        try:
            stmt = select(
                self.invoice_out_put.id,
                self.invoice_out_put.description,
                self.invoice_out_put.value_operation,
            ).where(self.invoice_out_put.id == id)

            result = db.session.execute(stmt).fetchall()

            if not result:
                return (
                    jsonify(
                        {
                            "status_code": 404,
                            "message_id": "out_put_finance_not_found",
                        }
                    ),
                    404,
                )

            return (
                jsonify(
                    {
                        "status_code": 200,
                        "data": Metadata(result).model_to_list(),
                        "message_id": "success_get_out_put_finance",
                    }
                ),
                200,
            )

        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error in get out put finance: \
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

    def update_out_put_finance(self, id: int, data: dict):
        try:
            stmt = (
                update(self.invoice_out_put)
                .where(self.invoice_out_put.id == id)
                .values(
                    description=data.get("description"),
                    value_operation=data.get("value_operation"),
                    types_payments=data.get("type_payments"),
                )
            )

            db.session.execute(stmt)
            db.session.commit()

            return (
                jsonify(
                    {
                        "status_code": 200,
                        "message_id": "success_update_out_put_finance",
                        "error": False,
                    }
                ),
                200,
            )

        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error in update out put finance: \
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

    def list_type_payments(self):
        try:
            stmt = select(
                self.finance_payments.id,
                func.upper(self.finance_payments.type_payments).label("type_payments"),
            ).where(~self.finance_payments.is_deleted)

            result = db.session.execute(stmt).fetchall()

            if not result:
                return (
                    jsonify(
                        {
                            "status_code": 404,
                            "message_id": "type_payments_not_found",
                        }
                    ),
                    404,
                )

            return (
                jsonify(
                    {
                        "status_code": 200,
                        "data": Metadata(result).model_to_list(),
                        "message_id": "success_list_type_payments",
                    }
                ),
                200,
            )

        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error in list type payments: \
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

    def list_summary_types_payments(self):
        try:
            stmt = (
                select(
                    self.finance_payments.type_payments,
                    func.sum(
                        self.products.value_operation
                        + self.box_accounting.value_operation
                    ).label("total_received"),
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
                .join(
                    self.finance_payments,
                    self.finance_payments.id == self.invoice.payments_id,
                )
                .where(self.schedule.is_check == True)
                .group_by(self.finance_payments.type_payments)
            )

            result = db.session.execute(stmt).fetchall()

            if not result:
                return (
                    jsonify(
                        {
                            "status_code": 404,
                            "message_id": "type_payments_not_found",
                        }
                    ),
                    404,
                )

            return (
                jsonify(
                    {
                        "status_code": 200,
                        "data": Metadata(result).model_to_list(),
                        "message_id": "success_list_summary_type_payments",
                    }
                ),
                200,
            )

        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error in list summary type payments: \
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

    def list_total_payments(self):
        try:
            stmt = (
                select(
                    func.sum(
                        self.products.value_operation
                        + self.box_accounting.value_operation
                    ).label("totals_received")
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
                .join(
                    self.finance_payments,
                    self.finance_payments.id == self.invoice.payments_id,
                )
                .where(self.schedule.is_check.is_(True))
            )

            result = db.session.execute(stmt).fetchall()

            if not result:
                return (
                    jsonify(
                        {
                            "status_code": 404,
                            "message_id": "total_payments_not_found",
                        }
                    ),
                    404,
                )

            return (
                jsonify(
                    {
                        "status_code": 200,
                        "data": Metadata(result).model_to_list(),
                        "message_id": "success_list_total_payments",
                    }
                ),
                200,
            )

        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error list totals payments: \
                {str(e)}\n{traceback.format_exc()}",
            )
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "internal_server_error",
                        "erro": True,
                    }
                ),
                500,
            )

    def list_out_put_exit_payments(self, data: dict):
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
                    self.invoice_out_put.id,
                    func.sum(self.invoice_out_put.value_operation).label("total_exit"),
                    self.invoice_out_put.description,
                    self.invoice_out_put.types_payments,
                )
                .where(self.invoice_out_put.is_deleted == False)
                .group_by(self.invoice_out_put.id)
            )

            if pagination_params.filter_by:
                filter_value = f"%{pagination_params.filter_by}%"
                try:
                    stmt = stmt.where(
                        or_(
                            func.unaccent(self.invoice_out_put.description).ilike(
                                func.unaccent(filter_value)
                            ),
                        )
                    )
                except Exception:
                    stmt = stmt.filter(
                        self.invoice_out_put.description.ilike(filter_value)
                    )

            totals = select(
                func.sum(self.invoice_out_put.value_operation).label("totals")
            ).where(self.invoice_out_put.is_deleted == False)

            total_count = db.session.execute(
                select(func.count()).select_from(stmt.subquery())
            ).scalar()

            paginated_stmt = stmt.offset(
                (pagination_params.current_page - 1) * pagination_params.rows_per_page
            ).limit(pagination_params.rows_per_page)

            result = db.session.execute(paginated_stmt).fetchall()
            result_totals = db.session.execute(totals).fetchone()

            if not result:
                return (
                    jsonify(
                        {
                            "status_code": 404,
                            "message_id": "total_payments_not_found",
                        }
                    ),
                    404,
                )

            metadata = pagination.build_metadata(total_count, pagination_params)
            return (
                jsonify(
                    {
                        "status_code": 200,
                        "totals:": Metadata(result_totals).model_to_list(),
                        "data": Metadata(result).model_to_list(),
                        "message_id": "success_list_out_put_exit_payments",
                        "erro": False,
                        "metadata": metadata,
                    }
                ),
                200,
            )

        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error in list out put exit payments: \
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

    def list_invoice_payments(self, data: dict):
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
                    self.invoice.id.label("invoice_id"),
                    self.user.username.label("username"),
                    self.products.description,
                    self.products.value_operation,
                    self.employees.username.label("employee_name"),
                    self.finance_payments.type_payments,
                )
                .select_from(self.box_accounting)
                .join(
                    self.invoice,
                    self.invoice.id == self.box_accounting.invoice_id,
                )
                .join(
                    self.schedule,
                    self.schedule.id == self.invoice.schedule_id,
                )
                .join(
                    self.user,
                    self.user.id == self.schedule.user_id,
                )
                .join(
                    self.products,
                    self.products.id == self.schedule.product_id,
                )
                .join(
                    self.employees,
                    self.employees.id == self.schedule.employee_id,
                )
                .join(
                    self.finance_payments,
                    self.finance_payments.id == self.invoice.payments_id,
                )
                .where(self.schedule.is_check.is_(True))
                .order_by(self.invoice.created_at.asc())
            )

            if pagination_params.filter_by:
                filter_value = f"%{pagination_params.filter_by}%"
                try:
                    stmt = stmt.where(
                        or_(
                            func.unaccent(self.user.username).ilike(
                                func.unaccent(filter_value)
                            ),
                            func.unaccent(self.employees.username).ilike(
                                func.unaccent(filter_value)
                            ),
                        )
                    )
                except Exception:
                    stmt = stmt.filter(self.user.username.ilike(filter_value))

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
                            "message_id": "invoice_payments_not_found",
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
                        "message_id": "success_list_invoice_payments",
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
                message=f"Error in list invoice payments: \
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

    def update_invoce_payments(self, invoce_id: int, data: dict):
        try:
            payments_id = int(data.get("payments_id"))
            tips = data.get("tips")
            value_operations = data.get("value_operations")

            if payments_id:
                # update payments
                update_invoice = (
                    update(self.invoice.payments_id)
                    .where(self.invoice.id == invoce_id)
                    .values(payments_id=payments_id)
                )
                db.session.execute(update_invoice)
                db.session.commit()

            if tips or value_operations:
                update_box_accounting = (
                    update(self.box_accounting)
                    .where(self.box_accounting.invoice_id == invoce_id)
                    .values(tips=tips, value_operations=value_operations)
                )
                db.session.execute(update_box_accounting)
                db.session.commit()

            return (
                jsonify(
                    {
                        "status_code": 200,
                        "message_id": "success_update_invoice_payments",
                        "error": False,
                    }
                ),
                200,
            )

        except Exception as e:
            print("coletando error", e)
            db.session.rollback()
            logdb(
                "error",
                message=f"Error in update invoice payments: \
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
