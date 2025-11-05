from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError

from src.db.database import db
from src.model.company import Company
from src.utils.metadata import ApiResponse


class CompanyService:
    def __init__(self, *args, **kwargs):
        self.db_session = db
        self.models = Company

    def add_company(self, company_data: dict) -> ApiResponse:
        try:
            stmt = insert(self.models).values(**company_data)
            self.db_session.execute(stmt)
            self.db_session.commit()
            return ApiResponse(success=True, message="Company added successfully.")
        except IntegrityError:
            self.db_session.rollback()
            return ApiResponse(success=False, message="Company with this email already exists.")
        except Exception:
            self.db_session.rollback()
            return ApiResponse(success=False, message="Error occurred while adding company.")
