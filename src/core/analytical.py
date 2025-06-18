# src/core/analytical.py

import traceback

from flask import jsonify
from sqlalchemy import select, func
from src.db.database import db
from src.model.model import ScheduleService, Products, Employee
from src.utils.log import logdb
from src.utils.metadata import Metadata


class AnalyticalCore:
    
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.schedule_service = ScheduleService
        self.products = Products
        self.employee = Employee
        
        
    def summary_client(self, user_id: int):
        try:
            # 1. Total de visitas
            total_visits_stmt = select(
                func.count(self.schedule_service.id).label("total_visits")
            ).where(
                self.schedule_service.is_check == True,
                self.schedule_service.user_id == user_id
            )

            # 2. Total gasto
            total_spent_stmt = (
                select(func.coalesce(func.sum(self.products.value_operation), 0).label("total_spent"))
                .select_from(self.schedule_service)
                .join(self.products, self.products.id == self.schedule_service.product_id)
                .where(
                    self.schedule_service.is_check == True,
                    self.schedule_service.user_id == user_id
                )
            )

            # 3. Tipos de cortes realizados
            cuts_stmt = (
                select(
                    self.products.description.label("corte"),
                    func.count(self.products.id).label("total_vezes")
                )
                .select_from(self.schedule_service)
                .join(self.products, self.products.id == self.schedule_service.product_id)
                .where(
                    self.schedule_service.is_check == True,
                    self.schedule_service.user_id == user_id
                )
                .group_by(self.products.description)
            )

            # 4. Barbeiros mais frequentes
            barbers_stmt = (
                select(
                    self.employee.username.label("barbeiro"),
                    func.count(self.employee.id).label("total_cortes")
                )
                .select_from(self.schedule_service)
                .join(self.employee, self.employee.id == self.schedule_service.employee_id)
                .where(
                    self.schedule_service.is_check == True,
                    self.schedule_service.user_id == user_id
                )
                .group_by(self.employee.username)
                .order_by(func.count(self.employee.id).desc())
            )

            total_visits = db.session.execute(total_visits_stmt).scalar()
            total_spent = db.session.execute(total_spent_stmt).scalar()
            cuts = db.session.execute(cuts_stmt).fetchall()
            barbers = db.session.execute(barbers_stmt).fetchall()

            return jsonify({
                "status_code": 200,
                "data": {
                    "total_visits": total_visits,
                    "total_spent": total_spent,
                    "cuts": Metadata(cuts).model_to_list(),
                    "barbers": Metadata(barbers).model_to_list(),
                },
                "error": False,
                "message_id": "success_summary_client",
            }), 200

        except Exception as e:
            logdb(
                "error",
                message=f"Error summary client shop: {e}\n{traceback.format_exc()}",
            )
            return jsonify({
                "status_code": 500,
                "message_id": "error_summary_client",
                "error": True,
            }), 500
