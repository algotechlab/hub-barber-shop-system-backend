from sqlalchemy import func, insert, select, update
from sqlalchemy.exc import IntegrityError

from src.db.database import db
from src.model.employee import Employee
from src.utils.metadata import ApiResponse, ModelSerializer
from src.utils.pagination import Pagination
from src.utils.utc import get_utc_now

EMPLOYEE_FIELDS = ["first_name", "last_name", "phone_number", "owner_id"]


class EmployeeService:
    def __init__(self, user_id: int, company_id: int, *args, **kwargs):
        self.db_session = db.session
        self.model = Employee
        self.user = user_id
        self.company_id = company_id

    def add_employee(self, employee_data: dict) -> tuple:
        try:
            stmt = insert(self.model).values(**employee_data)
            self.db_session.execute(stmt)
            self.db_session.commit()
            return ApiResponse(
                success=True, message="Employee added successfully.", status_code=201
            ).to_response()
        except IntegrityError:
            self.db_session.rollback()
            return ApiResponse(
                success=False,
                message="Employee with this phone number already exists.",
                status_code=409,
            ).to_response()
        except Exception:
            self.db_session.rollback()
            return ApiResponse(
                success=False, message="Error occurred while adding employee.", status_code=500
            ).to_response()

    def list_employees(self, data: dict) -> ApiResponse:
        try:
            pagination = Pagination(data)
            pagination_params, error = pagination.validate_params()
            if error:
                return ApiResponse(
                    status_code=400, message_id="invalid_pagination_params", error=True
                ).to_response()
            stmt = select(
                self.model.id,
                self.model.first_name,
                self.model.last_name,
                self.model.phone_number,
                self.model.is_active,
            ).where(~self.model.is_deleted)

            self.db_session.execute(stmt).all()
            if pagination_params.filter_by:
                filter_value = f"%{pagination_params.filter_by}%"
                try:
                    stmt = stmt.filter(
                        func.unaccent(self.model.first_name).ilike(func.unaccent(filter_value))
                    )
                except Exception:
                    stmt = stmt.filter(self.model.first_name.ilike(filter_value))

            sort_column = getattr(self.model, pagination_params.order_by, None)
            if sort_column:
                stmt = stmt.order_by(
                    sort_column.asc() if pagination_params.sort_by == "asc" else sort_column.desc()
                )

            total_count = db.session.execute(
                select(func.count()).select_from(stmt.subquery())
            ).scalar()

            paginated_stmt = stmt.offset(
                (pagination_params.current_page - 1) * pagination_params.rows_per_page
            ).limit(pagination_params.rows_per_page)

            result = db.session.execute(paginated_stmt).fetchall()
            metadata = pagination.build_metadata(total_count, pagination_params)
            serializer = ModelSerializer(result)

            return ApiResponse(
                status_code=200,
                data=serializer.to_list(),
                metadata=metadata if metadata else {},
                message_id="list_employees_success",
                error=False,
            ).to_response()
        except Exception:
            self.db_session.rollback()
            return ApiResponse(
                success=False, message="Error occurred while listing employees.", status_code=500
            ).to_response()

    def get_employee(self, employee_id: int) -> Employee | None:
        stmt = select(self.model).where(self.model.id == employee_id, ~self.model.is_deleted)
        result = self.db_session.execute(stmt).scalar_one_or_none()
        return result

    def update_employee(self, employee_id: int, update_data: dict) -> ApiResponse:
        try:
            stmt = (
                update(self.model)
                .where(self.model.id == employee_id, ~self.model.is_deleted)
                .values(**update_data, updated_at=get_utc_now())
            )
            result = self.db_session.execute(stmt)
            if result.rowcount == 0:
                return ApiResponse(
                    success=False, message="Employee not found.", status_code=404
                ).to_response()
            self.db_session.commit()
            return ApiResponse(
                success=True, message="Employee updated successfully.", status_code=200
            ).to_response()
        except IntegrityError:
            self.db_session.rollback()
            return ApiResponse(
                success=False, message="Employee with this email already exists.", status_code=409
            ).to_response()
        except Exception:
            self.db_session.rollback()
            return ApiResponse(
                success=False, message="Error occurred while updating employee.", status_code=500
            ).to_response()

    def delete_employee(self, employee_id: int) -> ApiResponse:
        try:
            stmt = (
                update(self.model)
                .where(self.model.id == employee_id, ~self.model.is_deleted)
                .values(is_deleted=True, updated_at=get_utc_now())
            )
            result = self.db_session.execute(stmt)
            if result.rowcount == 0:
                return ApiResponse(
                    success=False, message="Employee not found.", status_code=404
                ).to_response()
            self.db_session.commit()
            return ApiResponse(
                success=True, message="Employee deleted successfully.", status_code=200
            ).to_response()
        except Exception:
            self.db_session.rollback()
            return ApiResponse(
                success=False, message="Error occurred while deleting employee.", status_code=500
            ).to_response()
