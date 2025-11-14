from sqlalchemy import func, insert, select, update
from sqlalchemy.exc import IntegrityError

from src.db.database import db
from src.model.owner import Owner
from src.utils.metadata import ApiResponse, ModelSerializer
from src.utils.pagination import Pagination
from src.utils.utc import get_utc_now


OWNER_FIELDS = [
    "first_name",
    "last_name",
    "email",
    "phone_number",
]


class OwnerService:
    def __init__(self, *args, **kwargs):
        self.db_session = db.session
        self.model = Owner

    def add_owner(self, owner_data: dict) -> tuple:
        try:
            stmt = insert(self.model).values(**owner_data)
            self.db_session.execute(stmt)
            self.db_session.commit()
            return ApiResponse(
                success=True,
                message="Owner added successfully.",
                status_code=201,
            ).to_response()
        except IntegrityError:
            self.db_session.rollback()
            return ApiResponse(
                success=False,
                message="Owner with this email already exists.",
                status_code=409,
            ).to_response()
        except Exception:
            self.db_session.rollback()
            return ApiResponse(
                success=False,
                message="Error occurred while adding owner.",
                status_code=500,
            ).to_response()

    def list_owners(self, data: dict) -> ApiResponse:
        try:
            pagination = Pagination(data)
            pagination_params, error = pagination.validate_params()
            if error:
                return ApiResponse(
                    status_code=400,
                    message_id="invalid_pagination_params",
                    error=True,
                ).to_response()
            stmt = select(
                self.model.id,
                self.model.first_name,
                self.model.last_name,
                self.model.email,
                self.model.phone_number,
                self.model.is_active,
            ).where(~self.model.is_deleted)

            self.db_session.execute(stmt).all()
            if pagination_params.filter_by:
                filter_value = f"%{pagination_params.filter_by}%"
                try:
                    stmt = stmt.filter(
                        func.unaccent(self.model.first_name).ilike(
                            func.unaccent(filter_value)
                        )
                    )
                except Exception:
                    stmt = stmt.filter(
                        self.model.first_name.ilike(filter_value)
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
                message_id="list_owners_success",
                error=False,
            ).to_response()
        except Exception:
            return ApiResponse(
                status_code=500,
                message="Error processing list owners",
                error=True,
            ).to_response()

    def get_owner(self, owner_id: int) -> ApiResponse:
        try:
            stmt = select(
                self.model.id,
                self.model.first_name,
                self.model.last_name,
                self.model.email,
                self.model.phone_number,
            ).where(
                self.model.id.__eq__(owner_id),
                self.model.is_deleted.__eq__(False),
            )

            result = self.db_session.execute(stmt).first()
            if not result:
                return ApiResponse(
                    status_code=404, message="Owner not found", error=True
                ).to_response()

            return ApiResponse(
                status_code=200,
                data=result,
                message="Get owner success",
                error=False,
            ).to_response()
        except Exception:
            return ApiResponse(
                status_code=500,
                message="Error processing get owner",
                error=True,
            ).to_response()

    def update_owner(self, owner_id: int, update_data: dict) -> tuple:
        try:
            owner = (
                self.db_session.query(self.model)
                .filter_by(
                    id=owner_id,
                    is_deleted=False,
                )
                .first()
            )
            if not owner:
                return ApiResponse(
                    status_code=404, message="Owner not found", error=True
                ).to_response()

            filtered_update = {}
            for key, value in update_data.items():
                if (
                    value is not None
                    and key in OWNER_FIELDS
                    and hasattr(self.model, key)
                ):
                    setattr(owner, key, value)
                    filtered_update[key] = value

            if not filtered_update:
                return ApiResponse(
                    status_code=400,
                    message="No valid fields to update",
                    error=True,
                ).to_response()

            stmt = (
                update(self.model)
                .where(self.model.id == owner_id)
                .values(**filtered_update)
            )

            self.db_session.execute(stmt)
            self.db_session.commit()
            self.db_session.refresh(owner)
            return ApiResponse(
                status_code=200, message="Update successfully", error=False
            ).to_response()
        except Exception:
            self.db_session.rollback()
            return ApiResponse(
                status_code=500,
                message="Error processing update owner",
                error=True,
            ).to_response()

    def delete_owner(self, owner_id: int) -> ApiResponse:
        try:
            owner = (
                self.db_session.query(self.model)
                .filter_by(
                    id=owner_id,
                    is_deleted=False,
                )
                .first()
            )
            if not owner:
                return ApiResponse(
                    status_code=404, message="Owner not found", error=True
                ).to_response()
            stmt = (
                update(self.model)
                .where(self.model.id.__eq__(owner_id))
                .values(deleted_at=get_utc_now(), is_deleted=True)
            )

            self.db_session.execute(stmt)
            self.db_session.commit()

            return ApiResponse(
                status_code=200, message="Delete successfully", error=False
            ).to_response()
        except Exception:
            self.db_session.rollback()
            return ApiResponse(
                status_code=500,
                message="Error processing delete owner",
                error=True,
            ).to_response()
