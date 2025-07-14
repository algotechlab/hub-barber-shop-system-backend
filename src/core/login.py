# src/core/login.py
import traceback

from flask import jsonify
from flask_jwt_extended import create_access_token
from sqlalchemy import func, select
from werkzeug.security import check_password_hash, generate_password_hash

from src.db.database import db
from src.model.model import Employee, User
from src.utils.log import logdb
from src.utils.metadata import Metadata


class LoginCore:
    def __init__(self, *args, **kwargs):
        self.user = User
        self.email = None
        self.user_id = None
        self.employee = Employee

    def get_login(self, data: dict):
        user = self.user.query.filter_by(phone=data.get("phone")).first()

        if not user:
            return jsonify(
                {
                    "status_code": 404,
                    "message_id": "user_not_found",
                }
            ), 404

        self.user_id = user.id
        self.email = None

        stmt = select(
            self.user.id,
            self.user.username,
        ).where(self.user.id == self.user_id)

        result = db.session.execute(stmt).fetchone()

        try:
            access_token = create_access_token(
                identity={"id": self.user_id, "email": self.email}
            )
            db.session.commit()

            return jsonify(
                {
                    "status_code": 200,
                    "message_id": "user_logged_in_successfully",
                    "data": Metadata(result).model_to_list(),
                    "metadata": {"access_token": access_token},
                }
            )

        except Exception:
            logdb(
                "error",
                message=f"Error login employee.\n{traceback.format_exc()}",
            )
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "internal_error_on_login",
                }
            ), 500

    def reset_password_authorization(self, data: dict):
        try:
            new_password = generate_password_hash(
                password="123@dg", method="scrypt"
            )
            id = self.user.query.filter_by(id=data.get("id")).update(
                {"password": new_password, "updated_at": func.now()}
            )
            db.session.execute(id)
            db.session.commit()

            return jsonify(
                {
                    "status_code": 200,
                    "message_id": "resert_password_successfully",
                }
            )
        except Exception as e:
            logdb("error", message=str(e))
            return jsonify(
                {
                    "status_code": 500,
                    "message_id": "error_processing_reset_password",
                    "error": True,
                }
            )

    def get_login_employee(self, data: dict):
        try:
            phone = data.get("phone")
            password = data.get("password")
            employee = self.employee.query.filter_by(phone=phone).first()

            stmt = select(
                self.employee.id,
                self.employee.username,
                self.employee.role,
            ).where(~self.employee.is_deleted, self.employee.phone == phone)

            result = db.session.execute(stmt).fetchone()

            if not result:
                return jsonify(
                    {
                        "status_code": 404,
                        "message_id": "employee_not_found",
                    }
                ), 404

            is_valid = check_password_hash(employee.password, password)
            if is_valid:
                access_token = create_access_token(
                    identity={"id": result.id, "username": result.username}
                )
                return jsonify(
                    {
                        "status_code": 200,
                        "data": Metadata(result).model_to_list(),
                        "metadata": {"access_token": access_token},
                    }
                ), 200
            else:
                logdb(
                    "error",
                    message=f"Error login employee. \
                    \n{traceback.format_exc()}",
                )
                return jsonify(
                    {
                        "status_code": 401,
                        "message_id": "invalid_password",
                    }
                ), 401

        except Exception as e:
            print("Error coletado com sucesso", e)
            logdb(
                "error",
                message=f"Error login employee. \
                \n{traceback.format_exc()}",
            )
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "error_processing",
                    }
                ),
            ), 500
