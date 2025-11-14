from sqlalchemy import insert, update

from src.db.database import db
from src.model.product_employee import ProductsEmployees
from src.utils.metadata import ApiResponse
from src.utils.utc import get_utc_now


class ProductEmployeeService:
    def __init__(self, user_id: int, company_id, *args, **kwargs):
        self.model = ProductsEmployees
        self.db_session = db.session
        self.company_id = company_id
        self.user = user_id

    def add_product_employee(self, data: dict):
        try:
            stmt = insert(self.model).values(
                company_id=self.company_id, **data
            )
            self.db_session.execute(stmt)
            self.db_session.commit()

            return ApiResponse(
                success=True,
                message="Product relation of employee added successfully.",
                status_code=201,
            ).to_response()

        except Exception:
            self.db_session.rollback()
            return ApiResponse(
                success=False,
                message="Error occurred while adding employee.",
                status_code=500,
            ).to_response()

    def delete_product_employee(self, product_id: int, employee_id: int):
        try:
            stmt = (
                update(self.model)
                .where(
                    self.model.company_id.__eq__(self.company_id),
                    self.model.product_id.__eq__(product_id),
                    self.model.employee_id.__eq__(employee_id),
                )
                .values(
                    deleted_at=get_utc_now(),
                    deleted_by=self.user,
                    is_deleted=True,
                )
            )
            print(stmt)
            self.db_session.execute(stmt)
            self.db_session.commit()

            return ApiResponse(
                status_code=200, message="Delete successfully", error=False
            ).to_response()
        except Exception:
            self.db_session.rollback()
            return ApiResponse(
                success=False,
                message="Error occurred while deleting employee.",
                status_code=500,
            ).to_response()
