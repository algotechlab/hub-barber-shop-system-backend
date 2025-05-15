# src/core/employee.py

import traceback
from datetime import datetime

from flask import jsonify
from sqlalchemy import func, insert, select, update
from werkzeug.security import generate_password_hash

from src.db.database import db
from src.model.model import Employee
from src.utils.log import logdb
from src.utils.metadata import Metadata
from src.utils.pagination import Pagination


class EmployeeCore:
    def __init__(self, user_id: int, *args, **kwargs):
        self.employee = Employee
        self.user_id = user_id

    def add_employee(self, data: dict):
        try:
            # expect data format cpf and rf and phone
            cpf = data.get("cpf").replace(".", "").replace("-", "")
            rg = data.get("rg").replace(".", "").replace("-", "")
            phone = (
                data.get("phone")
                .replace("(", "")
                .replace(")", "")
                .replace("-", "")
            )
            data["cpf"] = cpf
            data["rg"] = rg
            data["phone"] = phone

            stmt = insert(self.employee).values(
                username=data.get("username"),
                cpf=data.get("cpf"),
                rg=data.get("phone"),
                date_of_birth=data.get("date_of_birth"),
                nickname=data.get("nickname"),
                email=data.get("email"),
                phone=data.get("phone"),
                password=generate_password_hash(
                    password=data.get("password"), method="scrypt"
                ),
            )

            db.session.execute(stmt)
            db.session.commit()

            return jsonify(
                {
                    "status_code": 200,
                    "message_id": "success_add_employee",
                    "error": False,
                }
            )
        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error add employee. {e}\n{traceback.format_exc()}",
            )
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "error_add_employee",
                    "error": True,
                }
            )

    def get_employee(self, id: int):
        try:
            stmt = select(
                self.employee.username,
                self.employee.cpf,
                self.employee.rg,
                func.to_char(self.employee.date_of_birth, "DD/MM/YYYY").label(
                    "date_of_birth"
                ),
                self.employee.nickname,
                self.employee.email,
                self.employee.phone,
            ).where(~self.employee.is_deleted, self.employee.id == id)

            result = db.session.execute(stmt).fetchall()

            if not result:
                return jsonify(
                    {
                        "status_code": 404,
                        "message_id": "employee_not_found",
                    }
                )

            return jsonify(
                {
                    "status_code": 200,
                    "data": Metadata(result).model_to_list(),
                    "message_id": "success_get_employee",
                    "error": False,
                }
            )

        except Exception as e:
            logdb(
                "error",
                message=f"Error get employee. {e}\n{traceback.format_exc()}",
            )
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "error_get_employee",
                    "error": True,
                }
            )

    def list_employees(self, data: dict):
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

            stmt = select(
                self.employee.id,
                self.employee.username,
                self.employee.cpf,
                self.employee.rg,
                self.employee.date_of_birth,
                self.employee.nickname,
                self.employee.email,
                self.employee.phone,
            ).where(~self.employee.is_deleted)

            # Filtro dinâmico com ILIKE e unaccent
            if pagination_params.filter_by:
                filter_value = f"%{pagination_params.filter_by}%"
                try:
                    stmt = stmt.filter(
                        func.unaccent(self.employee.username).ilike(
                            func.unaccent(filter_value)
                        )
                    )
                except Exception:
                    stmt = stmt.filter(
                        self.employee.username.ilike(filter_value)
                    )

            # Ordenação dinâmica
            sort_column = getattr(self.employee, pagination_params.order_by, None)
            if sort_column:
                stmt = stmt.order_by(
                    sort_column.asc()
                    if pagination_params.sort_by == "asc"
                    else sort_column.desc()
                )

            total_count = db.session.execute(
                select(func.count()).select_from(stmt.subquery())
            ).scalar()

            paginated_stmt = stmt.offset(
                (pagination_params.current_page - 1)
                * pagination_params.rows_per_page
            ).limit(pagination_params.rows_per_page)

            result = db.session.execute(paginated_stmt).fetchall()

            if not result:
                return jsonify(
                    {
                        "status_code": 404,
                        "message_id": "employee_not_found",
                    }
                )

            metadata = pagination.build_metadata(
                total_count, pagination_params
            )

            return jsonify(
                {
                    "status_code": 200,
                    "data": Metadata(result).model_to_list(),
                    "metadata": metadata if metadata else None,
                    "message_id": "success_list_employees",
                    "error": False,
                }
            )
        except Exception as e:
            logdb(
                "error",
                message=f"Error list employees. {e}\n{traceback.format_exc()}",
            )
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "error_list_employees",
                    "error": True,
                }
            )

    def update_employee(self, id: int, data: dict):
        try:
            if not id:
                return jsonify(
                    {
                        "status_code": 400,
                        "message_id": "not_id_found",
                    }
                )

            employee_fields = [
                "username",
                "cpf",
                "rg",
                "date_of_birth",
                "nickname",
                "email",
                "phone",
                "password",
            ]
            update_data = {}

            for key, value in data.items():
                if value is not None and key in employee_fields:
                    if key == "password" and value:
                        hashed_value = generate_password_hash(
                            value, method="scrypt"
                        )
                    update_data[key] = hashed_value

            if not update_data:
                return jsonify(
                    {
                        "status_code": 400,
                        "message_id": "no_valid_fields",
                        "error": True,
                    }
                )

            stmt = (
                update(self.employee)
                .where(~self.employee.is_deleted, self.employee.id == id)
                .values(**update_data)
            )

            db.session.execute(stmt)
            db.session.commit()

            return jsonify(
                {
                    "status_code": 200,
                    "message_id": "success_update_employee",
                    "error": False,
                }
            )

        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error edit employee. {e}\n{traceback.format_exc()}",
            )
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "error_update_employee",
                    "error": True,
                }
            )

    def delete_employee(self, id: int):
        try:
            if not id:
                return jsonify(
                    {
                        "status_code": 400,
                        "message_id": "not_id_found",
                        "error": True,
                    }
                )

            stmt = (
                update(self.employee)
                .where(~self.employee.is_deleted, self.employee.id == id)
                .values(
                    is_deleted=True,
                    deleted_at=datetime.now(),
                    deleted_by=self.user_id,
                )
            )
            db.session.execute(stmt)
            db.session.commit()

            return jsonify(
                {
                    "status_code": 200,
                    "message_id": "success_delete_employee",
                    "error": False,
                }
            )

        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=(
                    f"Error delete employee. {e}\n{traceback.format_exc()}"
                ),
            )
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "error_delete_employee",
                    "error": True,
                }
            )
