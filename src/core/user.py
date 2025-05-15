# src/core/user.py

import traceback

from flask import Response, jsonify
from sqlalchemy import func, insert, select
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from src.db.database import db
from src.model.model import User
from src.utils.log import logdb
from src.utils.metadata import Metadata
from src.utils.pagination import Pagination


class UserCore:
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.user = User

    def get_user(self, id: int):
        try:
            stmt = select(
                self.user.id,
                self.user.username,
                self.user.lastname,
                self.user.email,
                self.user.phone,
            ).where(~self.user.is_deleted, self.user.id == id)

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
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_processing_list_users",
            )

    def add_user(self, data: dict):
        try:
            if not data:
                return jsonify(
                    {
                        "status_code": 400,
                        "message_id": "not_parms_found",
                    }
                )

            if (
                not data.get("username")
                or not data.get("lastname")
                or not data.get("email")
                or not data.get("password")
            ):
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="not_parms_found",
                )
            stmt = (
                insert(self.user)
                .values(
                    username=data.get("username"),
                    lastname=data.get("lastname"),
                    email=data.get("email"),
                    password=generate_password_hash(
                        password=data.get("password"), method="scrypt"
                    ),
                    phone=data.get("phone"),
                )
                .returning(self.user.id, self.user.username, self.user.email)
            )

            result = db.session.execute(stmt).fetchone()
            db.session.commit()

            return Response().response(
                status_code=200,
                error=False,
                data={
                    "id": result.id,
                    "username": result.username,
                    "email": result.email,
                },
                message_id="register_successfully",
            )
        except IntegrityError:
            db.session.rollback()
            logdb(
                "error",
                message=f" \
                Error warning rollback user: \
                IntegrityError\n{traceback.format_exc()}",
            )
            return Response().response(
                status_code=409,
                error=True,
                message_id="email_already_exists",
            )
        except Exception as e:
            logdb(
                "error",
                message=f"Error listing users: {e}\n{traceback.format_exc()}",
            )
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "error_processing_add_user",
                    "error": True,
                }
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
            user_fields = [
                "username",
                "lastname",
                "email",
                "password",
                "phone",
            ]
            for key, value in data.items():
                if value is not None and key in user_fields:
                    if key == "password" and value:
                        hashed_value = generate_password_hash(
                            value, method="scrypt"
                        )
                    if hasattr(user, key):
                        setattr(user, key, hashed_value)

            db.session.commit()

            return Response().response(
                status_code=200,
                error=False,
                message_id="update_successfully",
            )
        except Exception as e:
            logdb(
                "error",
                message=f"Error updating user: {e}\n{traceback.format_exc()}",
            )
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "error_processing_update_user",
                    "error": True,
                }
            )

    def delete(self, id: int):
        try:
            user = self.user.query.filter_by(id=id).first()
            user.is_deleted = True
            db.session.commit()

            return Response().response(
                status_code=200,
                error=False,
                message_id="delete_successfully",
            )
        except Exception as e:
            logdb(
                "error",
                message=f"Error delete user: {e}\n{traceback.format_exc()}",
            )
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "error_processing_delete_user",
                    "error": True,
                }
            )
