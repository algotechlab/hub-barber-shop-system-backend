# src/core/user.py
import hashlib
import traceback

from flask import jsonify
from flask_jwt_extended import create_access_token
from sqlalchemy import func, insert, select, update
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from src.db.database import db
from src.model.model import User
from src.utils.log import logdb
from src.utils.metadata import Metadata
from src.utils.pagination import Pagination

USER_FIELDS = [
    "username",
    "lastname",
    "password",
    "phone",
]


class UserCore:
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.user = User

    # compact token
    def compact_token(self, token: str):
        return hashlib.sha256(token.encode()).hexdigest()

    def get_user(self, id: int):
        try:
            stmt = select(
                self.user.id,
                self.user.username,
                self.user.lastname,
                self.user.phone,
            ).where(self.user.id == id)

            result = db.session.execute(stmt).fetchall()

            if not result:
                return jsonify(
                    {
                        "status_code": 404,
                        "message_id": "user_not_found",
                    }
                )

            return jsonify(
                {
                    "status_code": 200,
                    "data": Metadata(result).model_to_list(),
                }
            )
        except Exception as e:
            logdb(
                "error",
                message=f"Error get user: {e}\n{traceback.format_exc()}",
            )
            return (
                jsonify(
                    (
                        {
                            "status_code": 500,
                            "message_id": "error_processing_list_users",
                            "error": True,
                        }
                    )
                ),
                500,
            )

    def add_user(self, data: dict):
        try:
            if not data:
                return (
                    jsonify(
                        (
                            {
                                "status_code": 400,
                                "message_id": "not_parms_found",
                            }
                        )
                    ),
                    400,
                )
            if (
                not data.get("username")
                or not data.get("lastname")
                or not data.get("password")
            ):
                return (
                    jsonify(
                        (
                            {
                                "status_code": 400,
                                "message_id": "not_parms_found",
                            }
                        )
                    ),
                    400,
                )

            stmt = (
                insert(self.user)
                .values(
                    username=data.get("username"),
                    lastname=data.get("lastname"),
                    password=generate_password_hash(
                        password=data.get("password"), method="scrypt"
                    ),
                    phone=data.get("phone"),
                )
                .returning(self.user.id, self.user.username)
            )

            result = db.session.execute(stmt).fetchone()
            access_token = create_access_token(
                identity={"id": result.id}
            )
            db.session.commit()

            return (
                jsonify(
                    (
                        {
                            "status_code": 200,
                            "data": {
                                "id": result.id,
                                "username": result.username,
                            },
                            "access_token": self.compact_token(access_token),
                            "message_id": "register_successfully",
                            "error": False,
                        }
                    )
                ),
                200,
            )
        except IntegrityError:
            db.session.rollback()
            logdb(
                "error",
                message=f" \
                Error warning rollback user: \
                IntegrityError\n{traceback.format_exc()}",
            )
            return (
                jsonify(
                    (
                        {
                            "status_code": 409,
                            "message_id": "email_already_exists",
                            "error": True,
                        }
                    )
                ),
                409,
            )
        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error listing users: {e}\n{traceback.format_exc()}",
            )
            return (
                jsonify(
                    (
                        {
                            "status_code": 500,
                            "message_id": "error_processing_add_user",
                            "error": True,
                        }
                    )
                ),
                500,
            )

    def list_users(self, data: dict):
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
                self.user.id,
                self.user.username,
                self.user.lastname,
                self.user.phone,
            ).where(~self.user.is_deleted)

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

            sort_column = getattr(self.user, pagination_params.order_by, None)
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

            # Executa a consulta
            result = db.session.execute(paginated_stmt).fetchall()

            if not result:
                return jsonify(
                    {"status_code": 404, "message_id": "users_not_found"}
                )

            metadata = pagination.build_metadata(
                total_count, pagination_params
            )

            return jsonify(
                {
                    "status_code": 200,
                    "data": Metadata(result).model_to_list(),
                    "metadata": metadata if metadata else {},
                    "message_id": "list_users_success",
                }
            )

        except Exception as e:
            logdb(
                "error",
                message=f"Error listing users: {e}\n{traceback.format_exc()}",
            )
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "error_processing_list_users",
                }
            )

    def update_user(self, id: int, data: dict):
        try:
            user = self.user.query.filter_by(id=id).first()

            if not user:
                return (
                    jsonify(
                        (
                            {
                                "status_code": 404,
                                "message_id": "user_not_found",
                                "error": True,
                            }
                        )
                    ),
                    404,
                )

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

            stmt = (
                update(self.user)
                .where(~self.user.is_deleted, self.user.id == id)
                .values(**update_data)
            )

            db.session.execute(stmt)
            db.session.commit()

            return (
                jsonify(
                    (
                        {
                            "status_code": 200,
                            "message_id": "update_successfully",
                            "error": False,
                        }
                    )
                ),
                200,
            )
        except Exception as e:
            logdb(
                "error",
                message=f"Error updating user: {e}\n{traceback.format_exc()}",
            )
            return (
                jsonify(
                    (
                        {
                            "status_code": 500,
                            "message_id": "error_processing_update_user",
                            "error": True,
                        }
                    )
                ),
                500,
            )

    def delete(self, id: int):
        try:
            user = self.user.query.filter_by(id=id).first()
            user.is_deleted = True
            db.session.commit()

            return (
                jsonify(
                    (
                        {
                            "status_code": 200,
                            "message_id": "delete_successfully",
                            "error": False,
                        }
                    )
                ),
                200,
            )
        except Exception as e:
            logdb(
                "error",
                message=f"Error delete user: {e}\n{traceback.format_exc()}",
            )
            return (
                jsonify(
                    (
                        {
                            "status_code": 500,
                            "message_id": "error_processing_delete_user",
                            "error": True,
                        }
                    )
                ),
                500,
            )
