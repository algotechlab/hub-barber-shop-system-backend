# src/core/employee.py

import traceback
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import jsonify
from sqlalchemy import func, insert, select, update, literal_column
from sqlalchemy.orm import aliased
from werkzeug.security import generate_password_hash

from src.db.database import db
from src.model.model import Employee, ScheduleService, Products
from src.utils.log import logdb
from src.utils.metadata import Metadata
from src.utils.pagination import Pagination

EMPLOYEE_FIELDS = [
    "id",
    "username",
    "cpf",
    "rg",
    "date_of_birth",
    "nickname",
    "email",
    "phone",
]


class EmployeeCore:
    def __init__(self, user_id: int, *args, **kwargs):
        self.employee = Employee
        self.schedule = ScheduleService
        self.product = Products
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

            return (
                jsonify(
                    (
                        {
                            "status_code": 200,
                            "message_id": "success_add_employee",
                            "error": False,
                        }
                    )
                ),
                200,
            )
        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error add employee. {e}\n{traceback.format_exc()}",
            )
            return (
                jsonify(
                    (
                        {
                            "status_code": 500,
                            "message_id": "error_add_employee",
                            "error": True,
                        }
                    )
                ),
                500,
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

            return (
                jsonify(
                    (
                        {
                            "status_code": 200,
                            "data": Metadata(result).model_to_list(),
                            "message_id": "success_get_employee",
                            "error": False,
                        }
                    )
                ),
                200,
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
                return (
                    jsonify(
                        (
                            {
                                "status_code": 400,
                                "message_id": "invalid_pagination_params",
                                "error": True,
                            }
                        )
                    ),
                    400,
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
            sort_column = getattr(
                self.employee, pagination_params.order_by, None
            )
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
                return (
                    jsonify(
                        (
                            {
                                "status_code": 404,
                                "message_id": "employee_not_found",
                            }
                        )
                    ),
                    404,
                )

            metadata = pagination.build_metadata(
                total_count, pagination_params
            )

            return (
                jsonify(
                    (
                        {
                            "status_code": 200,
                            "data": Metadata(result).model_to_list(),
                            "metadata": metadata if metadata else None,
                            "message_id": "success_list_employees",
                            "error": False,
                        }
                    )
                ),
                200,
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

    def list_avaliable_emploees(self):
        ## TODO - checar a possibilidade disso aqui
        try:
            if hour.tzinfo is None:
                hour = hour.replace(tzinfo=ZoneInfo("UTC"))
                hour_utc = hour.astimezone(ZoneInfo("UTC"))

            # Aliases para clareza
            Schedule = aliased(self.schedule)
            Product = aliased(self.product)
            Employee = aliased(self.employee)

            # Subquery com todos os agendamentos ativos
            subq = (
                select(
                    Schedule.employee_id.label("employee_id"),
                    Schedule.time_register.label("inicio"),
                    (Schedule.time_register + Product.time_to_spend).label("fim"),
                )
                .join(Product, Schedule.product_id == Product.id)
                .where(Schedule.is_deleted.is_(False))
                .where(Schedule.is_check.is_(False))
                .where(Product.is_deleted.is_(False))
                .subquery()
            )

            # Consulta principal: retorna funcionários que NÃO têm agendamento conflitante
            stmt = (
                select(Employee.id, Employee.username)
                .where(Employee.is_deleted.is_(False))
                .where(
                    ~db.session.query(literal_column("1"))
                    .select_from(subq)
                    .filter(subq.c.employee_id == Employee.id)
                    .filter(subq.c.inicio <= hour_utc)
                    .filter(hour_utc < subq.c.fim)
                    .exists()
                )
                .order_by(Employee.username)
            )

            result = db.session.execute(stmt).fetchall()
            
            if not result:
                return (
                    jsonify(
                        (
                            {
                                "status_code": 404,
                                "message_id": "employee_not_found",
                            }
                        )
                    ),
                    404,
                )


            return (
                jsonify(
                    (
                        {
                            "status_code": 200,
                            "data": Metadata(result).model_to_list(),
                            "message_id": "success_list_employees",
                            "error": False,
                        }
                    )
                ),
                200,
            )
            
        except Exception as e:
            logdb(
                "error",
                message=f"Error list avaliable employees. {e}\n{traceback.format_exc()}",
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
                return (
                    jsonify(
                        (
                            {
                                "status_code": 400,
                                "message_id": "not_id_found",
                            }
                        )
                    ),
                    400,
                )

            employee = self.employee.query.filter_by(id=id).first()
            if not employee:
                return (
                    jsonify(
                        (
                            {
                                "status_code": 404,
                                "message_id": "employee_not_found",
                                "error": True,
                            }
                        )
                    ),
                    404,
                )

            update_data = {}

            for key, value in data.items():
                if value is not None and key in EMPLOYEE_FIELDS:
                    updated_value = (
                        generate_password_hash(value, method="scrypt")
                        if key == "password"
                        else value
                    )

                    if hasattr(employee, key):
                        setattr(employee, key, updated_value)
                        update_data[key] = updated_value

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

            return (
                jsonify(
                    (
                        {
                            "status_code": 200,
                            "message_id": "success_delete_employee",
                            "error": False,
                        }
                    )
                ),
                200,
            )

        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=(
                    f"Error delete employee. {e}\n{traceback.format_exc()}"
                ),
            )
            return (
                jsonify(
                    (
                        {
                            "status_code": 500,
                            "message_id": "error_delete_employee",
                            "error": True,
                        }
                    )
                ),
                500,
            )
