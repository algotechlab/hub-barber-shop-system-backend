from flask_jwt_extended import create_access_token
from sqlalchemy import func, insert, select, update
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from src.db.database import db
from src.model.user import User
from src.utils.metadata import ApiResponse, ModelSerializer
from src.utils.pagination import Pagination
from src.utils.utc import get_utc_now

USER_FIELDS = [
    "username",
    "phone",
    "email",
    "password",
]


class UserService:
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.user = User

    def get_user(self, id: int):
        try:
            stmt = select(
                self.user.id,
                self.user.username,
                self.user.email,
                self.user.phone,
            ).where(self.user.id.__eq__(id), ~self.user.is_deleted)

            result = db.session.execute(stmt).first()
            if not result:
                return ApiResponse(
                    status_code=404, message_id="user_not_found", error=True
                ).to_response()

            return ApiResponse(
                status_code=200,
                data=result,
                message_id="get_user_success",
                error=False,
            ).to_response()
        except Exception:
            return ApiResponse(
                status_code=500, message_id="error_processing_get_user", error=True
            ).to_response()

    def add_user(self, data: dict):
        try:
            if not data.get("username"):
                return ApiResponse(
                    status_code=400, message_id="not_parms_found", error=True
                ).to_response()

            stmt = (
                insert(self.user)
                .values(
                    username=data.get("username"),
                    phone=data.get("phone"),
                    email=data.get("email"),
                    hashed_password=generate_password_hash(data.get("password"), method="scrypt"),
                )
                .returning(self.user.id, self.user.username)
            )

            result = db.session.execute(stmt).fetchone()
            access_token = create_access_token(identity={"id": result.id})
            db.session.commit()

            user_data = {"id": result.id, "username": result.username}

            return ApiResponse(
                status_code=200,
                data=user_data,
                access_token=access_token,
                message_id="register_successfully",
                error=False,
            ).to_response()
        except IntegrityError:
            db.session.rollback()
            return ApiResponse(
                status_code=409, message_id="email_already_exists", error=True
            ).to_response()
        except Exception:
            db.session.rollback()
            return ApiResponse(
                status_code=500, message_id="error_processing_add_user", error=True
            ).to_response()

    def list_users(self, data: dict):
        try:
            pagination = Pagination(data)
            pagination_params, error = pagination.validate_params()
            if error:
                return ApiResponse(
                    status_code=400, message_id="invalid_pagination_params", error=True
                ).to_response()

            stmt = select(
                self.user.id,
                self.user.username,
                self.user.phone,
            ).where(~self.user.is_deleted)

            if pagination_params.filter_by:
                filter_value = f"%{pagination_params.filter_by}%"
                try:
                    stmt = stmt.filter(
                        func.unaccent(self.user.username).ilike(func.unaccent(filter_value))
                    )
                except Exception:
                    stmt = stmt.filter(self.user.username.ilike(filter_value))

            sort_column = getattr(self.user, pagination_params.order_by, None)
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
            serialized_data = serializer.to_list()

            return ApiResponse(
                status_code=200,
                data=serialized_data,
                metadata=metadata if metadata else {},
                message_id="list_users_success",
                error=False,
            ).to_response()

        except Exception:
            return ApiResponse(
                status_code=500, message_id="error_processing_list_users", error=True
            ).to_response()

    def update_user(self, id: int, data: dict):
        try:
            user = self.user.query.filter_by(id=id, is_deleted=False).first()

            if not user:
                return ApiResponse(
                    status_code=404, message_id="user_not_found", error=True
                ).to_response()

            update_data = {}
            for key, value in data.items():
                if value is not None and key in USER_FIELDS:
                    updated_value = (
                        generate_password_hash(value, method="scrypt")
                        if key == "password"
                        else value
                    )
                    if hasattr(user, key):
                        setattr(user, key, updated_value)
                        update_data[key] = updated_value

            stmt = update(self.user).where(self.user.id == id).values(**update_data)

            db.session.execute(stmt)
            db.session.commit()

            return ApiResponse(
                status_code=200, message_id="update_successfully", error=False
            ).to_response()
        except Exception:
            return ApiResponse(
                status_code=500, message_id="error_processing_update_user", error=True
            ).to_response()

    def delete(self, id: int):
        try:
            user = self.user.query.filter_by(id=id).first()
            if not user:
                return ApiResponse(
                    status_code=404, message_id="user_not_found", error=True
                ).to_response()

            user.is_deleted = True
            user.deleted_at = get_utc_now()
            db.session.commit()
            db.session.refresh(user)
            return ApiResponse(
                status_code=200, message_id="delete_successfully", error=False
            ).to_response()
        except Exception as e:
            print(e)
            return ApiResponse(
                status_code=500, message_id="error_processing_delete_user", error=True
            ).to_response()
