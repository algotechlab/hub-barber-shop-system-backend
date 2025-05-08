# src/core/user.py

from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from werkzeug.security import generate_password_hash
from sqlalchemy import func, insert
from src.db.database import db
from src.model.model import User
from src.service.response import Response
from src.utils.metadata import Metadata
from src.utils.pagination import Pagination
from src.utils.log import logdb


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
                self.user.phone
            ).where(self.user.id == id, self.user.is_deleted == False)

            result = db.session.execute(stmt).fetchall()

            if not result:
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="user_not_found",
                )

            return Response().response(
                status_code=200,
                data=Metadata(result).model_to_list(),
            )
        except Exception as e:
            logdb("error", message=str(e))
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_processing_list_users",
            )

    def add_user(self, data: dict):
        try:
            if not data:
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="something_went_wrong",
                )

            if not data.get("username") or not data.get("lastname") or not data.get("email") or not data.get("password"):
                return Response().response(
                    status_code=400,
                    error=True,
                    message_id="not_parms_found",
                )
            stmt = insert(self.user).values(
                username=data.get("username"),
                lastname=data.get("lastname"),
                email=data.get("email"),
                password=generate_password_hash(password=data.get("password"), method="scrypt"),
                phone=data.get("phone"),
            ).returning(self.user.id, self.user.username, self.user.email)
            
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
        except IntegrityError as uq:
            db.session.rollback()
            logdb("warning", message=str(uq))
            return Response().response(
                status_code=409,
                error=True,
                message_id="email_already_exists",
            )
        except Exception as e:
            logdb("error", message=str(e))
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_processing",
            )

    def list_users(self, data: dict):
        try:
            current_page = int(data.get("current_page", 1))
            rows_per_page = int(data.get("rows_per_page", 10))
            
            if current_page < 1:
                current_page = 1
            if rows_per_page < 1:
                rows_per_page = 1

            pagination = Pagination().pagination(
                current_page=current_page,
                rows_per_page=rows_per_page,
                sort_by=data.get("sort_by", ""),
                order_by=data.get("order_by", ""),
                filter_by=data.get("filter_by", ""),
                filter_value=data.get("filter_value", "")
            )
            
            stmt = select(
                self.user.id,
                self.user.username,
                self.user.lastname,
                self.user.phone
                
            ).where(
                self.user.is_deleted == False
            )
            
            # Filtro dinâmico com ILIKE e unaccent
            if pagination["filter_by"]:
                filter_value = f"%{pagination['filter_by']}%"
                stmt = stmt.filter(
                    db.or_(
                        func.unaccent(self.user.username).ilike(func.unaccent(filter_value)),
                    )
                )

            # Ordenação dinâmica
            if pagination["order_by"] and pagination["sort_by"]:
                sort_column = getattr(self.user, pagination["order_by"], None)
                if sort_column:
                    stmt = stmt.order_by(
                        sort_column.asc() if pagination["sort_by"] == "asc" else sort_column.desc()
                    )
            else:
                stmt = stmt.order_by(self.user.id.desc())  # Ordem padrão por id DESC

            # pagination
            paginated_stmt = stmt.offset(pagination["offset"]).limit(pagination["limit"])
            result = db.session.execute(paginated_stmt).fetchall()

            if not result:
                return Response().response(
                    status_code=404,
                    error=True,
                    message_id="users_list_not_found",
                    exception="Not found"
                )

            return Response().response(
                status_code=200,
                data=Metadata(result).model_to_list(),
            )

        except Exception as e:
            logdb("error", message=str(e))
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_processing",
            )

    def update_user(self, id: int, data: dict):
        try:
            
            user = self.user.query.filter_by(id=id).first()
            user_fields = ["username", "lastname", "email", "password", "phone"]
            for key, value in data.items():
                if value is not None and key in user_fields:
                    if key == "password" and value:
                        value = generate_password_hash(value, method="scrypt")
                    if hasattr(user, key):
                        setattr(user, key, value)
        
            db.session.commit()
            
            return Response().response(
                status_code=200,
                error=False,
                message_id="update_successfully",
            )
        except Exception as e:
            logdb("error", message=str(e))
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_processing",
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
            logdb("error", message=str(e))
            return Response().response(
                status_code=500,
                error=True,
                message_id="error_processing",
            )
