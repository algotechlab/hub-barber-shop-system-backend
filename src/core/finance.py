# src/core/finance.py

import traceback

from flask import jsonify
from sqlalchemy import func, select

from src.db.database import db
from src.model.model import (
    BoxAccounting,
    Invoice,
    InvoiceOutPut,
    Payments,
    Products,
    ScheduleService,
)
from src.utils.log import logdb
from src.utils.metadata import Metadata


class FinanceCore:
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.finance_payments = Payments
        self.invoice = Invoice
        self.box_accounting = BoxAccounting
        self.schedule = ScheduleService
        self.products = Products
        self.invoice_out_put = InvoiceOutPut

    def list_type_payments(self):
        try:
            stmt = select(
                self.finance_payments.id,
                func.upper(self.finance_payments.type_payments).label(
                    "type_payments"
                ),
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

            return jsonify(
                {
                    "status_code": 200,
                    "data": Metadata(result).model_to_list(),
                    "message_id": "success_list_type_payments",
                }
            ), 200

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

            return jsonify(
                {
                    "status_code": 200,
                    "data": Metadata(result).model_to_list(),
                    "message_id": "success_list_summary_type_payments",
                }
            ), 200

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

            return jsonify(
                {
                    "status_code": 200,
                    "data": Metadata(result).model_to_list(),
                    "message_id": "success_list_total_payments",
                }
            ), 200

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

    def list_out_put_exit_payments(self):
        try:
            stmt = select(
                func.sum(self.invoice_out_put.value_operation).label(
                    "total_exit"
                )
            ).where(self.invoice_out_put.is_deleted == False)

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

            return jsonify(
                {
                    "status_code": 200,
                    "data": Metadata(result).model_to_list(),
                    "message_id": "success_list_out_put_exit_payments",
                }
            ), 200

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
