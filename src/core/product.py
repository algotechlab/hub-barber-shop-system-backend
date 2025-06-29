# src/core/product.py

import os
import traceback
from datetime import datetime, timedelta

from flask import jsonify, url_for
from sqlalchemy import func, select, text, update
from werkzeug.utils import secure_filename

from src.db.database import db
from src.model.model import Products
from src.utils.log import logdb
from src.utils.pagination import Pagination
from src.utils.product import UploadImageProduct

PRODUCTS_FIELDS = [
    "description",
    "value_operation",
    "time_to_spend",
    "commission",
    "category",
]


MINUTES = 59
SECONDS = 59


UPLOAD_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "static"
)


class ProductCore:
    def __init__(self, user_id: int, *args, **kwargs):
        self.products = Products
        self.user_id = user_id

    def _parse_time_to_spend(self, hhmmss: str) -> timedelta:
        try:
            if not hhmmss or not isinstance(hhmmss, str):
                raise ValueError("time_to_spend must be a non-empty string")

            h, m, s = map(int, hhmmss.split(":"))
            if h < 0 or m < 0 or s < 0 or m > MINUTES or s > SECONDS:
                raise ValueError("Invalid time format or values")

            return timedelta(hours=h, minutes=m, seconds=s)
        except ValueError as e:
            raise ValueError(f"Invalid time_to_spend format: {str(e)}")

    def add_product(self, data: dict, image_file):
        try:
            if not data:
                return (
                    jsonify(
                        {
                            "status_code": 400,
                            "message_id": "not_parms_found",
                            "error": True,
                        }
                    ),
                    400,
                )

            if image_file:
                uploader = UploadImageProduct(
                    description=data.get("description"),
                    user_id=self.user_id,
                    created_at=datetime.now(),
                )
                image_path = uploader.save_image(image_file)
                image_url = url_for(
                    "static", filename=image_path, _external=True
                )

            stmt = self.products.__table__.insert().values(
                description=data.get("description"),
                value_operation=float(data.get("value_operation")),
                time_to_spend=self._parse_time_to_spend(
                    data.get("time_to_spend")
                ),
                commission=float(data.get("commission")),
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
                        "data": {
                            "description": data.get("description"),
                            "image_url": image_url,
                        },
                    }
                ),
                200,
            )

        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error add product: {e}\n{traceback.format_exc()}",
            )
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "error_processing_add_product",
                        "error": True,
                        "traceback": str(e),
                    }
                ),
                500,
            )

    def list_products(self, data: dict):
        try:
            pagination = Pagination(data)
            pagination_params, error = pagination.validate_params()
            if error:
                return {
                    "status_code": 400,
                    "message_id": "invalid_pagination_params",
                    "error": True,
                }, 400

            stmt = select(
                self.products.id,
                func.initcap(func.trim(self.products.description)).label(
                    "description"
                ),
                self.products.value_operation,
                func.to_char(
                    self.products.time_to_spend, text("'HH24:MI:SS'")
                ).label("time_to_spend"),
                self.products.commission,
                func.initcap(func.trim(self.products.category)).label(
                    "category"
                ),
            ).where(~self.products.is_deleted)

            if pagination_params.filter_by:
                filter_value = f"%{pagination_params.filter_by}%"
                stmt = stmt.filter(
                    func.unaccent(self.products.description).ilike(
                        func.unaccent(filter_value)
                    )
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

            result = db.session.execute(paginated_stmt).fetchall()

            if not result:
                return {
                    "status_code": 404,
                    "message_id": "products_not_found",
                    "error": True,
                }, 404

            metadata = pagination.build_metadata(
                total_count, pagination_params
            )

            formatted_result = []
            base_upload_dir = os.path.join("src", "static", "uploads")
            for row in result:
                image_url = None
                description = secure_filename(
                    row.description.replace(" ", "_")
                )
                for root, dirs, files in os.walk(base_upload_dir):
                    if f"product_images_{description}" in root:
                        for file in files:
                            print("Coletando o file", file)
                            if file.endswith((".png", ".jpg", ".jpeg")):
                                relative_path = os.path.relpath(
                                    os.path.join(root, file),
                                    os.path.join("src", "static"),
                                ).replace(os.sep, "/")
                                image_url = url_for(
                                    "static",
                                    filename=relative_path,
                                    _external=True,
                                )
                                break
                        if image_url:
                            break
                row_dict = row._asdict()
                formatted_result.append({**row_dict, "image_url": image_url})

            return {
                "status_code": 200,
                "data": formatted_result,
                "metadata": metadata if metadata else None,
                "error": False,
            }, 200

        except Exception as e:
            logdb(
                "error",
                message=f"Error list products: {e}\n{traceback.format_exc()}",
            )
            return {
                "status_code": 500,
                "message_id": "something_went_wrong",
                "traceback": traceback.format_exc(),
                "error": True,
            }, 500

    def update_product(self, id: int, data: dict):
        try:
            if not data:
                return (
                    jsonify(
                        {
                            "status_code": 400,
                            "message_id": "not_parms_found",
                            "error": True,
                        }
                    ),
                    400,
                )

            product = db.session.query(self.products).filter_by(id=id).first()

            if not product:
                return (
                    jsonify(
                        {
                            "status_code": 404,
                            "message_id": "product_not_found",
                            "error": True,
                        }
                    ),
                    404,
                )

            for key, value in data.items():
                if value is not None and key in PRODUCTS_FIELDS:
                    parsed_value = (
                        self._parse_time_to_spend(value)
                        if key == "time_to_spend"
                        else value
                    )
                    if hasattr(product, key):
                        setattr(product, key, parsed_value)

            db.session.commit()

            return (
                jsonify(
                    {
                        "status_code": 200,
                        "message_id": "product_updated_successfully",
                        "error": False,
                    }
                ),
                200,
            )

        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error update product: {e}\n{traceback.format_exc()}",
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

    def delete_product(self, id: int):
        try:
            stmt = (
                update(self.products)
                .where(self.products.id == id)
                .values(
                    is_deleted=True,
                    deleted_at=datetime.now(),
                    deleted_by=self.user_id,
                )
            )
            db.session.execute(stmt)
            db.session.commit()

            return (
                jsonify(
                    {
                        "status_code": 200,
                        "message_id": "success_delete_product",
                        "error": False,
                    }
                ),
                200,
            )

        except Exception as e:
            logdb(
                "error",
                message=f"Error delete product: {e}\n{traceback.format_exc()}",
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
