from sqlalchemy import func, insert, select, update
from sqlalchemy.exc import IntegrityError

from src.db.database import db
from src.model.company import Company
from src.utils.metadata import ApiResponse, ModelSerializer
from src.utils.pagination import Pagination
from src.utils.utc import get_utc_now


COMPANY_FIELDS = [
    "name",
    "email",
    "phone_number",
    "color",
    "slug",
]


class CompanyService:
    def __init__(self, *args, **kwargs):
        self.db_session = db.session
        self.model = Company

    def add_company(self, data: dict) -> ApiResponse:
        try:
            stmt = insert(self.model).values(**data)
            self.db_session.execute(stmt)
            self.db_session.commit()
            return ApiResponse(
                success=True, message="Company added successfully.", status_code=201
            ).to_response()
        except IntegrityError:
            self.db_session.rollback()
            return ApiResponse(
                status_code=400, message_id="company_already_exists", error=True
            ).to_response()
        except Exception:
            self.db_session.rollback()
            return ApiResponse(
                status_code=500, message_id="something_went_wrong", error=True
            ).to_response()

    def list_companies(self, data: dict) -> ApiResponse:
        try:
            pagination = Pagination(data)
            pagination_params, error = pagination.validate_params()
            if error:
                return ApiResponse(
                    status_code=400, message_id="invalid_pagination_params", error=True
                ).to_response()
            stmt = select(
                self.model.id,
                self.model.name,
                self.model.email,
                self.model.phone_number,
                self.model.color,
                self.model.slug,
                self.model.owner_id,
            ).where(~self.model.is_deleted)

            self.db_session.execute(stmt).all()
            if pagination_params.filter_by:
                filter_value = f"%{pagination_params.filter_by}%"
                try:
                    stmt = stmt.filter(
                        func.unaccent(self.model.name).ilike(func.unaccent(filter_value))
                    )
                except Exception:
                    stmt = stmt.filter(self.model.name.ilike(filter_value))

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
                message_id="list_companies_success",
                error=False,
            ).to_response()
        except Exception:
            return ApiResponse(
                status_code=500, message="Error processing list companies", error=True
            ).to_response()

    def update_company(self, company_id: int, update_data: dict) -> tuple:
        try:
            company = (
                self.db_session.query(self.model)
                .filter_by(
                    id=company_id,
                    is_deleted=False,
                )
                .first()
            )
            if not company:
                return ApiResponse(
                    status_code=404, message="Company not found", error=True
                ).to_response()

            filtered_update = {}
            for key, value in update_data.items():
                if value is not None and key in COMPANY_FIELDS and hasattr(self.model, key):
                    setattr(company, key, value)
                    filtered_update[key] = value

            if not filtered_update:
                return ApiResponse(
                    status_code=400, message="No valid fields to update", error=True
                ).to_response()

            stmt = update(self.model).where(self.model.id == company_id).values(**filtered_update)

            self.db_session.execute(stmt)
            self.db_session.commit()
            self.db_session.refresh(company)
            return ApiResponse(
                status_code=200, message="Update successfully", error=False
            ).to_response()
        except Exception:
            self.db_session.rollback()
            return ApiResponse(
                status_code=500, message="Error processing update owner", error=True
            ).to_response()

    def delete_company(self, company_id: int) -> ApiResponse:
        try:
            company = (
                self.db_session.query(self.model)
                .filter_by(
                    id=company_id,
                    is_deleted=False,
                )
                .first()
            )
            if not company:
                return ApiResponse(
                    status_code=404, message="Company not found", error=True
                ).to_response()
            stmt = (
                update(self.model)
                .where(self.model.id == company_id)
                .values(deleted_at=get_utc_now(), is_deleted=True)
            )

            self.db_session.execute(stmt)
            self.db_session.commit()

            return ApiResponse(
                status_code=200, message="Delete successfully", error=False
            ).to_response()
        except Exception as e:
            print("Coletnado o error:", e)
            self.db_session.rollback()
            return ApiResponse(
                status_code=500, message="Error processing delete company", error=True
            ).to_response()
