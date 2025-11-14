from sqlalchemy import func, insert, select, update

from src.db.database import db
from src.model.employee import Employee
from src.model.product import Product
from src.model.schedule import Schedule
from src.model.user import User
from src.utils.metadata import ApiResponse, ModelSerializer
from src.utils.pagination import Pagination
from src.utils.utc import get_utc_now


SCHEDULE_FIELDS = [
    "time_register",
    "employee_id",
    "product_id",
]


class ScheduleService:
    def __init__(self, user_id: int, company_id: int, *args, **kwargs):
        self.db_session = db.session
        self.company_id = company_id
        self.user_id = user_id
        self.model = Schedule
        self.products = Product
        self.employee = Employee
        self.user = User

    def add_schedule(self, schedule_data: dict):
        try:
            stmt = insert(self.model).values(
                company_id=self.company_id,
                user_id=self.user_id,
                **schedule_data,
            )
            self.db_session.execute(stmt)
            self.db_session.commit()

            return ApiResponse(
                success=True,
                message="Schedule added successfully.",
                status_code=201,
            ).to_response()

        except Exception:
            self.db_session.rollback()
            return ApiResponse(
                success=False,
                message="Error occurred while adding employee.",
                status_code=500,
            ).to_response()

    def list_schedule(self, data: dict) -> ApiResponse:
        try:
            pagination = Pagination(data)
            pagination_params, error = pagination.validate_params()
            if error:
                return ApiResponse(
                    status_code=400,
                    message_id="invalid_pagination_params",
                    error=True,
                ).to_response()

            stmt = (
                select(
                    self.model.id,
                    self.model.time_register,
                    self.employee.id.label("employee_id"),
                    self.products.id.label("product_id"),
                    self.products.description.label("product_name"),
                    func.to_char(
                        self.products.time_to_spend, "HH24:MI:SS"
                    ).label("time_to_spend"),
                    self.user.phone.label("phone"),
                    self.user.username.label("name_client"),
                    (
                        self.model.time_register + self.products.time_to_spend
                    ).label("end_time"),
                    self.employee.first_name.label("name_employee"),
                )
                .join(
                    self.employee,
                    self.model.employee_id.__eq__(self.employee.id),
                )
                .join(
                    self.products,
                    self.model.product_id.__eq__(self.products.id),
                )
                .join(self.user, self.model.user_id.__eq__(self.user.id))
                .where(
                    self.model.is_deleted.__eq__(False),
                    self.model.is_check.__eq__(False),
                    self.model.company_id.__eq__(self.company_id),
                )
            )

            self.db_session.execute(stmt).all()
            if pagination_params.filter_by:
                filter_value = f"%{pagination_params.filter_by}%"
                try:
                    stmt = stmt.filter(
                        func.unaccent(self.user.username).ilike(
                            func.unaccent(filter_value)
                        )
                    )
                except Exception:
                    stmt = stmt.filter(self.user.username.ilike(filter_value))

            sort_column = getattr(self.model, pagination_params.order_by, None)
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
            metadata = pagination.build_metadata(
                total_count, pagination_params
            )
            serializer = ModelSerializer(result)

            return ApiResponse(
                status_code=200,
                data=serializer.to_list(),
                metadata=metadata if metadata else {},
                message_id="list_schedule_success",
                error=False,
            ).to_response()
        except Exception:
            return ApiResponse(
                status_code=500,
                message="Error processing list owners",
                error=True,
            ).to_response()

    def get_schedule(self, user_id: int):
        try:
            stmt = (
                select(
                    self.model.id,
                    self.model.time_register,
                    self.employee.id.label("employee_id"),
                    self.products.id.label("product_id"),
                    self.products.description.label("product_name"),
                    func.to_char(
                        self.products.time_to_spend, "HH24:MI:SS"
                    ).label("time_to_spend"),
                    self.user.phone.label("phone"),
                    self.user.username.label("name_client"),
                    (
                        self.model.time_register + self.products.time_to_spend
                    ).label("end_time"),
                    self.employee.first_name.label("name_employee"),
                )
                .join(
                    self.employee,
                    self.model.employee_id.__eq__(self.employee.id),
                )
                .join(
                    self.products,
                    self.model.product_id.__eq__(self.products.id),
                )
                .join(self.user, self.model.user_id.__eq__(self.user.id))
                .where(
                    self.model.company_id.__eq__(self.company_id),
                    self.model.user_id.__eq__(user_id),
                    self.model.is_deleted.__eq__(False),
                    self.model.is_check.__eq__(False),
                )
            )
            result = self.db_session.execute(stmt).first()
            if not result:
                return ApiResponse(
                    status_code=404, message="Schedule not found", error=True
                ).to_response()

            return ApiResponse(
                status_code=200,
                data=result,
                message="Get schedule success",
                error=False,
            ).to_response()
        except Exception:
            return ApiResponse(
                status_code=500,
                message="Error processing get schedule",
                error=True,
            ).to_response()

    def update_schedule(self, schedule_id: int, update_data: dict):
        try:
            schedule = (
                self.db_session.query(self.model)
                .filter_by(
                    id=schedule_id,
                    company_id=self.company_id,
                    is_deleted=False,
                )
                .first()
            )
            if not schedule:
                return ApiResponse(
                    status_code=404, message="employee not found", error=True
                ).to_response()

            filtered_update = {}
            for key, value in update_data.items():
                if (
                    value is not None
                    and key in SCHEDULE_FIELDS
                    and hasattr(self.model, key)
                ):
                    setattr(schedule, key, value)
                    filtered_update[key] = value

            if not filtered_update:
                return ApiResponse(
                    status_code=400,
                    message="No valid fields to update",
                    error=True,
                ).to_response()

            stmt = (
                update(self.model)
                .where(
                    self.model.id.__eq__(schedule_id),
                    self.model.company_id.__eq__(self.company_id),
                    self.model.is_deleted.__eq__(False),
                )
                .values(
                    updated_at=get_utc_now(),
                    updated_by=self.user_id,
                    **filtered_update,
                )
            )

            self.db_session.execute(stmt)
            self.db_session.commit()
            return ApiResponse(
                success=True,
                message="Schedule updated successfully.",
                status_code=200,
            ).to_response()
        except Exception as e:
            print("Colentaod o erro do schedule:", e)
            return ApiResponse(
                status_code=500,
                message="Error processing update schedule",
                error=True,
            ).to_response()

    def delete_schedule(self, schedule_id: int):
        try:
            schedule = (
                self.db_session.query(self.model)
                .filter_by(
                    id=schedule_id,
                    company_id=self.company_id,
                    is_deleted=False,
                )
                .first()
            )
            if not schedule:
                return ApiResponse(
                    status_code=404, message="schedule not found", error=True
                ).to_response()

            stmt = (
                update(self.model)
                .where(
                    self.model.company_id.__eq__(self.company_id),
                    self.model.id.__eq__(schedule_id),
                )
                .values(
                    deleted_at=get_utc_now(),
                    deleted_by=self.user_id,
                    is_deleted=True,
                )
            )

            self.db_session.execute(stmt)
            self.db_session.commit()

            return ApiResponse(
                status_code=200, message="Delete successfully", error=False
            ).to_response()
        except Exception:
            self.db_session.rollback()
            return ApiResponse(
                success=False,
                message="Error occurred while deleting employee.",
                status_code=500,
            ).to_response()
