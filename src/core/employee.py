# src/core/employee.py

import traceback

from datetime import datetime
from werkzeug.security import generate_password_hash
from src.db.database import db
from sqlalchemy import insert, select, func, update
from src.model.model import Employee
from src.service.response import Response
from src.utils.metadata import Metadata
from src.utils.pagination import Pagination
from src.utils.log import logdb

class EmployeeCore:
    def __init__(self, user_id: int, *args, **kwargs):
        self.employee = Employee
        self.user_id = user_id
        
    def add_employee(self, data: dict):
        try:
            # expect data format cpf and rf and phone
            cpf = data.get("cpf").replace(".", "").replace("-", "")
            rg = data.get("rg").replace(".", "").replace("-", "")
            phone = data.get("phone").replace("(", "").replace(")", "").replace("-", "")
            data["cpf"] = cpf
            data["rg"] = rg
            data["phone"] = phone
            
            stmt = insert(self.employee).values(
                username=data.get("username"),
                cpf=data.get("email"),
                rg=data.get("phone"),
                date_of_birth=data.get("date_of_birth"),
                nickname=data.get("nickname"),
                email=data.get("email"),
                phone=data.get("phone"),
                password=generate_password_hash(password=data.get("password"), method="scrypt"),
            )
            
            db.session.execute(stmt)
            db.session.commit()
            return Response().response(
                status_code=200,
                error=False,
                message_id="success_add_employee",
            )
            
        except Exception as e:
            db.session.rollback()
            logdb("error", message=f"Error add employee. {e}\n{traceback.format_exc()}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_add_employee",
            )
    
    def get_employee(self, id: int):
        try:
            stmt = select(
                self.employee.username,
                self.employee.cpf,
                self.employee.rg,
                func.to_char(self.employee.date_of_birth, 'DD/MM/YYYY').label("date_of_birth"),
                self.employee.nickname,
                self.employee.email,
                self.employee.phone
            ).where(
                self.employee.id == id, self.employee.is_deleted == False
            )
            
            result = db.session.execute(stmt).fetchall()
            
            if not result:
                return Response().response(
                    status_code=404,
                    error=True,
                    message_id="employee_not_found",
                    exception="Not found"
                )
            
            return Response().response(
                status_code=200,
                error=False,
                data=Metadata(result).model_to_list(),
                message_id="success_get_employee",
            )

        except Exception as e:
            logdb("error", message=f"Error get employee. {e}\n{traceback.format_exc()}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_get_employee",
            )
    
    def list_employees(self, data: dict):
        try:
            current_page = int(data.get("current_page", 1))
            rows_per_page = int(data.get("rows_per_page", 10))
            
            if current_page < 1:
                current_page = 1
            if rows_per_page < 1:
                rows_per_page = 1

            pagination = Pagination().pagination(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=data.get("sort_by", ""),
                order_by=data.get("order_by", ""),
                filter_by=data.get("filter_by", ""),
                filter_value=data.get("filter_value", "")
            )
            
            stmt = select(
                self.employee.id,
                self.employee.username,
                self.employee.cpf,
                self.employee.rg,
                self.employee.date_of_birth,
                self.employee.nickname,
                self.employee.email,
                self.employee.phone
                ).where( self.employee.is_deleted == False )
            
            # Filtro dinâmico com ILIKE e unaccent
            if pagination["filter_by"]:
                filter_value = f"%{pagination['filter_by']}%"
                stmt = stmt.filter(
                    db.or_(
                        func.unaccent(self.employee.username).ilike(func.unaccent(filter_value)),
                    )
                )
            
            # Ordenação dinâmica
            if pagination["order_by"] and pagination["sort_by"]:
                sort_column = getattr(self.employee, pagination["order_by"], None)
                if sort_column:
                    stmt = stmt.order_by(
                        sort_column.asc() if pagination["sort_by"] == "asc" else sort_column.desc()
                    )
            else:
                stmt = stmt.order_by(self.employee.id.desc())  # Ordem padrão por id DESC
                
            # pagination
            paginated_stmt = stmt.offset(pagination["offset"]).limit(pagination["limit"])
            result = db.session.execute(paginated_stmt).fetchall()
            
            if not result:
                return Response().response(
                    status_code=404,
                    error=True,
                    message_id="employee_not_found",
                    exception="Not found"
                )
            
            metadata = Pagination().metadata(
                current_page=current_page,
                total_pages=round(len(result) / rows_per_page),
                total_rows=len(result),
                rows_per_page=rows_per_page,
                sort_by=pagination["sort_by"],
                order_by=pagination["order_by"],
                filter_by=pagination["filter_by"],
                filter_value=pagination["filter_value"],
                total=len(result)
            )
            
            total = db.session.execute(select(func.count(self.employee.id))).scalar()
            
            metadata = Pagination().metadata(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=pagination["sort_by"],
                order_by=pagination["order_by"],
                filter_by=pagination["filter_by"],
                total=total
            )
            return Response().response(
                status_code=200,
                error=False,
                data=Metadata(result).model_to_list(),
                metadata=metadata,
            )
        except Exception as e:
            logdb("error", message=f"Error list employees. {e}\n{traceback.format_exc()}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_list_employees",
            )
    
    def update_employee(self, id: int, data: dict):
        try:
            if not id:
                return Response().response(
                    status_code=404,
                    error=True,
                    message_id="is_required_id",
                    exception="Is required id"
                )

            employee_fields = ['username', 'cpf', 'rg', 'date_of_birth', 'nickname', 'email', 'phone', 'password']
            update_data = {}

            for key, value in data.items():
                if value is not None and key in employee_fields:
                    if key == "password" and value:
                        value = generate_password_hash(value, method="scrypt")
                    update_data[key] = value

            if not update_data:
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="no_valid_fields",
                    exception="No valid fields to update"
                )

            stmt = (update(self.employee).where(self.employee.id == id, self.employee.is_deleted == False).values(**update_data))

            db.session.execute(stmt)
            db.session.commit()

            return Response().response(
                status_code=200,
                error=False,
                message_id="success_update_employee",
            )

        except Exception as e:
            db.session.rollback()
            logdb("error", message=f"Error edit employee. {e}\n{traceback.format_exc()}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_update_employee",
            )

    def delete_employee(self, id: int):
        try:
            if not id:
                return Response().response(
                    status_code=404,
                    error=True,
                    message_id="is_required_id",
                    exception="Is required id"
                )
            stmt = (update(
                self.employee
            ).where(
                self.employee.id == id, self.employee.is_deleted == False
            ).values(is_deleted=True, deleted_at=datetime.now(), deleted_by=self.user_id))
            db.session.execute(stmt)
            db.session.commit()
            return Response().response(
                status_code=200,
                error=False,
                message_id="success_delete_employee",
            )
        except Exception as e:
            db.session.rollback()
            logdb("error", message=f"Error delete employee. {e}\n{traceback.format_exc()}")
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_delete_employee",
            )