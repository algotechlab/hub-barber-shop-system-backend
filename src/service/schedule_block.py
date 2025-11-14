from sqlalchemy import func, insert, select, update

from src.db.database import db
from src.model.employee import Employee
from src.model.schedule_block import ScheduleBlock
from src.utils.metadata import ApiResponse, ModelSerializer
from src.utils.pagination import Pagination
from src.utils.utc import get_utc_now


class BlockService:
    def __init__(self, user_id: int, company_id: int, *args, **kwargs):
        self.db_session = db.session
        self.company_id = company_id
        self.user_id = user_id
        self.model = ScheduleBlock
        self.employee = Employee

    def add_block(self, block_data: dict) -> ApiResponse:
        try:
            stmt = insert(self.model).values(
                company_id=self.company_id,
                **block_data,
            )
            self.db_session.execute(stmt)
            self.db_session.commit()

            return ApiResponse(
                success=True,
                message="Schedule block added successfully.",
                status_code=201,
            ).to_response()

        except Exception:
            self.db_session.rollback()
            return ApiResponse(
                success=False,
                message="Error occurred while adding employee.",
                status_code=500,
            ).to_response()

    def list_blocks(self, data: dict) -> ApiResponse:
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
                    self.model.id.label("block_id"),
                    self.employee.first_name.label("first_name"),
                    self.employee.last_name.label("last_name"),
                    self.model.start_time,
                    self.model.end_time,
                )
                .join(
                    self.employee,
                    self.model.employee_id.__eq__(self.employee.id),
                )
                .where(
                    self.model.is_deleted.__eq__(False),
                    self.model.company_id.__eq__(self.company_id),
                    self.employee.is_deleted.__eq__(False),
                )
            )

            self.db_session.execute(stmt).all()
            if pagination_params.filter_by:
                filter_value = f"%{pagination_params.filter_by}%"
                try:
                    stmt = stmt.filter(
                        func.unaccent(self.employee.first_name).ilike(
                            func.unaccent(filter_value)
                        )
                    )
                except Exception:
                    stmt = stmt.filter(
                        self.employee.first_name.ilike(filter_value)
                    )

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
                message_id="list_schedule_block_success",
                error=False,
            ).to_response()
        except Exception:
            return ApiResponse(
                status_code=500,
                message="Error processing list owners",
                error=True,
            ).to_response()

    def delete_block(self, block_id: int) -> ApiResponse:
        try:
            block = (
                self.db_session.query(self.model)
                .filter_by(
                    id=block_id,
                    company_id=self.company_id,
                    is_deleted=False,
                )
                .first()
            )
            if not block:
                return ApiResponse(
                    status_code=404,
                    message="schedule block not found",
                    error=True,
                ).to_response()

            stmt = (
                update(self.model)
                .where(
                    self.model.company_id.__eq__(self.company_id),
                    self.model.id.__eq__(block_id),
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
