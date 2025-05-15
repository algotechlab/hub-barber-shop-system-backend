# src/core/product.py

import traceback
from datetime import datetime, timedelta

from flask import jsonify
from sqlalchemy import func, insert, select, text

from src.db.database import db
from src.model.model import Products, ProductsEmployee
from src.utils.log import logdb
from src.utils.metadata import Metadata
from src.utils.pagination import Pagination


class ProductCore:

    def __init__(self, user_id: int, *args, **kwargs):
        self.products = Products
        self.products_employee = ProductsEmployee
        self.user_id = user_id

    def _parse_time_to_spend(self, hhmmss: str) -> datetime:
        h, m, s = map(int, hhmmss.split(":"))
        duration = timedelta(hours=h, minutes=m, seconds=s)
        base = datetime(1970, 1, 1)
        return base + duration

    def add_product(self, data: dict):
        try:
            if not data:
                return (
                    jsonify(
                        {
                            "status_code": 400,
                            "message_id": "not_parms_found",
                        }
                    )
                ), 400

            stmt = insert(self.products).values(
                description=data.get("description"),
                value_operation=data.get("value_operation"),
                time_to_spend=self._parse_time_to_spend(
                    data.get("time_to_spend")
                ),
                commission=data.get("commission"),
                category=data.get("category"),
            )
            db.session.execute(stmt)
            db.session.commit()

            return (
                jsonify(
                    {
                        "status_code": 200,
                        "message_id": "success_add_product",
                        "error": False,
                    }
                ),
                200,
            )

        except Exception as e:
            logdb(
                "error",
                message=f"Error add product: {e}\n{traceback.format_exc()}",
            )
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "error_prcessing_add_product",
                        "error": True,
                    }
                ),
                500,
            )

    def list_products(self, data: dict):
        try:
            pagination = Pagination(data)
            pagination_params, error = pagination.validate_params()
            if error:
                return (
                    jsonify(
                        {
                            "status_code": 400,
                            "message_id": "invalid_pagination_params",
                            "error": True,
                        },
                    ),
                    400,
                )

            stmt = select(
                self.products.id,
                self.products.description,
                self.products.value_operation,
                func.to_char(
                    self.products.time_to_spend, text("'HH24:MI:SS'")
                ).label("time_to_spend"),
                self.products.commission,
                self.products.category,
            ).where(
                ~self.products.is_deleted,
            )

            if pagination_params.filter_by:
                filter_value = f"%{pagination_params.filter_by}%"
                try:
                    stmt = stmt.filter(
                        func.unaccent(self.products.description).ilike(
                            func.unaccent(filter_value)
                        )
                    )
                except Exception:
                    stmt = stmt.filter(
                        self.products.description.ilike(filter_value)
                    )

            sort_column = getattr(
                self.products, pagination_params.order_by, None
            )
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
                return (
                    jsonify(
                        {
                            "status_code": 404,
                            "message_id": "products_not_found",
                        },
                    ),
                    404,
                )

            metadata = pagination.build_metadata(
                total_count, pagination_params
            )

            return (
                jsonify(
                    (
                        {
                            "status_code": 200,
                            "data": Metadata(result).model_to_list(),
                            "metadata": metadata if metadata else None,
                            "error": False,
                        }
                    ),
                ),
                200,
            )

        except Exception as e:
            logdb(
                "error",
                message=f"Error list products: \
                {e}\n{traceback.format_exc()}",
            )
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "something_went_wrong",
                        "traceback": traceback.format_exc(),
                        "error": True,
                    }
                ),
                500,
            )

    def update_product(self, id: int, data: dict): ...

    def delete_product(self, id: int): ...

    def add_product_employee(self, data: dict): ...

    def delete_product_employee(self, id: int): ...
