# src/core/user.py
from sqlalchemy import select
from werkzeug.security import generate_password_hash

from src.db.database import db
from src.model.model import User
from src.service.response import Response
from src.utils.metadata import Metadata


class UserCore:

    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.user = User

    def get_user(self, id: int):
        try:
            stmt = select(self.user.id, self.user.name, self.user.phone).where(self.user.id == id, self.user.is_deleted == False)

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
            db.session.rollback()
            print("", e)

    def add_user(self, data: dict):
        try:
            ...

        except Exception as e:
            ...

    def list_users(self, data: dict):
        try:
            ...

        except Exception as e:
            ...

    def update_user(self, id: int, data: dict):
        ...

    def delete(self, id: int):
        ...
