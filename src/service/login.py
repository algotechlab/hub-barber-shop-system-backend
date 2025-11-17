from flask_jwt_extended import create_access_token
from sqlalchemy import select
from werkzeug.security import check_password_hash

from src.auth.hash_compact import CompactHash
from src.db.database import db
from src.model.company import Company
from src.model.employee import Employee
from src.model.owner import Owner
from src.model.user import User
from src.utils.metadata import ApiResponse, ModelSerializer


class LoginService:
    def __init__(self, *args, **kwargs):
        self.db_session = db.session
        self.user = User
        self.employee = Employee
        self.owner = Owner
        self.company = Company

    def login_owner(self, data: dict) -> ApiResponse:
        try:
            query = (
                select(
                    self.owner.id.label("owner_id"),
                    self.owner.first_name,
                    self.owner.last_name,
                    self.owner.hashed_password,
                    self.company.email.label("company_email"),
                    self.company.id.label("company_id"),
                    self.company.slug,
                    self.company.name,
                )
                .select_from(self.owner)
                .join(self.company, self.company.owner_id == self.owner.id)
                .where(
                    self.owner.phone_number.__eq__(data["phone_number"]),
                    self.owner.is_deleted.is_(False),
                )
            )
            owner = self.db_session.execute(query).first()
            if not owner:
                return ApiResponse(
                    success=False,
                    message="Email not found.",
                    status_code=401,
                ).to_response()

            if not check_password_hash(
                owner.hashed_password, data["hashed_password"]
            ):
                return ApiResponse(
                    success=False,
                    message="Senha inválida.",
                    status_code=401,
                ).to_response()

            access_token = create_access_token(
                identity=str(owner.owner_id),
                additional_claims={
                    "role": "owner",
                    "first_name": owner.first_name,
                    "last_name": owner.last_name,
                    "company": owner.company_id,
                    "company_email": owner.company_email,
                },
            )

            compact = CompactHash.compact_token(access_token)
            serializer = ModelSerializer(owner)

            return ApiResponse(
                success=True,
                status_code=200,
                message="login_successful",
                data={
                    "token": access_token,
                    "token_hash": compact,
                    "owner": serializer.to_dict(),
                },
            ).to_response()

        except Exception as e:
            self.db_session.rollback()
            return ApiResponse(
                success=False,
                message="Error processing login.",
                error=str(e),
                status_code=500,
            ).to_response()

    def login_user(self, data: dict) -> ApiResponse:
        try:
            user = (
                self.db_session.query(self.user)
                .filter_by(phone=data["phone"], is_deleted=False)
                .first()
            )
            if not user:
                return ApiResponse(
                    success=False,
                    message="User not found.",
                    status_code=401,
                ).to_response()

            if not check_password_hash(
                user.hashed_password, data["hashed_password"]
            ):
                return ApiResponse(
                    success=False,
                    message="Password invalid.",
                    status_code=401,
                ).to_response()

            access_token = create_access_token(
                identity=str(user.id),
                additional_claims={
                    "id": user.id,
                    "first_name": user.username,
                    "company_id": user.company_id,
                },
            )

            compact = CompactHash.compact_token(access_token)
            serializer = ModelSerializer(user)

            return ApiResponse(
                success=True,
                status_code=200,
                message="login_successful",
                data={
                    "token": access_token,
                    "token_hash": compact,
                    "user": serializer.to_dict(),
                },
            ).to_response()

        except Exception as e:
            self.db_session.rollback()
            return ApiResponse(
                success=False,
                message="Error processing login.",
                error=str(e),
                status_code=500,
            ).to_response()

    def login_employee(self, data: dict) -> ApiResponse:
        try:
            employee = (
                self.db_session.query(self.employee)
                .filter_by(phone_number=data["phone_number"], is_deleted=False)
                .first()
            )
            if not employee:
                return ApiResponse(
                    success=False,
                    message="Employee not found.",
                    status_code=401,
                ).to_response()

            if not check_password_hash(
                employee.hashed_password, data["hashed_password"]
            ):
                return ApiResponse(
                    success=False,
                    message="Password invalid.",
                    status_code=401,
                ).to_response()

            access_token = create_access_token(
                identity=str(employee.id),
                additional_claims={
                    "role": "employee",
                    "id": employee.id,
                    "first_name": employee.first_name,
                    "last_name": employee.last_name,
                    "company_id": employee.company_id,
                },
            )

            compact = CompactHash.compact_token(access_token)
            serializer = ModelSerializer(employee)

            return ApiResponse(
                success=True,
                status_code=200,
                message="login_successful",
                data={
                    "token": access_token,
                    "token_hash": compact,
                    "employee": serializer.to_dict(),
                },
            ).to_response()

        except Exception as e:
            self.db_session.rollback()
            return ApiResponse(
                success=False,
                message="Error processing login.",
                error=str(e),
                status_code=500,
            ).to_response()
