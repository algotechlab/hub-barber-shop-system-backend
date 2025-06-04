# src/core/finance.py

import traceback

from sqlalchemy import select, func

from flask import jsonify
from src.db.database import db
from src.utils.log import logdb
from src.model.model import Payments, Invoice, BoxAccounting
from src.utils.metadata import Metadata
from src.utils.pagination import Pagination

class FinanceCore:
    
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.finance_payments = Payments
        self.invoice = Invoice
        self.box_accounting = BoxAccounting

    def list_type_payments(self):
        try:
            stmt = select(
                self.finance_payments.id,
                func.upper(self.finance_payments.type_payments)
                .label("type_payments"),
            ).where(
                ~self.finance_payments.is_deleted
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
                    "message_id": "success_list_type_payments",
                }
            ), 200
            
        except Exception as e:
            logdb(
                "error",
                message=f"Error in list type payments: \
                {str(e)}\n{traceback.format_exc()}",
            )
            db.session.rollback()
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