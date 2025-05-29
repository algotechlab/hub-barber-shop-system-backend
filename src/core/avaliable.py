# src/core/avaliable.py

import os
import traceback

from flask import jsonify
from sqlalchemy import func, select, text, update, insert

from src.db.database import db
from src.model.model import Avaliable, User
from src.utils.log import logdb
from src.utils.pagination import Pagination
from src.utils.metadata import Metadata




class AvaliableCore:
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.avaliable = Avaliable
        self.user = User
        
    def count_start(self):
        try:
            stmt = select(
                func.count(self.avaliable.star).label("count_star")
            )
            
            result = db.session.execute(stmt).fetchone()
            
            if not result:
                return (
                    jsonify(
                        {
                            "status_code": 404,
                            "message_id": "count_not_found",
                        }
                    ),
                    404,
                )
            
            return jsonify(
                {
                    "status_code": 200,
                    "message_id": "success_count_start",
                    "data": Metadata(result).model_to_list(),
                }
            ), 200
            
        except Exception as e:
            logdb(
                "error",
                message=f"Error list count start: {e}\n{traceback.format_exc()}",
            )
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "error_processing_list_count_start",
                        "error": True,
                        "traceback": str(e),
                    }
                ),
                500,
            )

    def list_avaliable(self, data: dict):
        try:
            pagination = Pagination(data)
            pagination_params, error = pagination.validate_params()
            
            stmt = select(
                func.upper(self.user.username).label("username"),
                func.upper(self.avaliable.observer).label("observer"),
                self.avaliable.star
            ).join(
                self.user, self.avaliable.user_id == self.user.id
            )
            
            sort_column = getattr(
                self.avaliable, pagination_params.order_by, None
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

            if not result:
                return (
                    jsonify(
                        {
                            "status_code": 404,
                            "message_id": "list_avaliable_not_found",
                        }
                    ),
                    404,
                )

            return jsonify(
                {
                    "status_code": 200,
                    "message_id": "success_list_avaliable",
                    "data": Metadata(result).model_to_list(),
                    "metadata": metadata if metadata else "",
                }
            ), 200

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

    def add_avaliable(self, data: dict):
        try:
            stmt = insert(
                self.avaliable
            ).values(
                observer=data.get("observer"),
                star=data.get("star"),
                product_id=data.get("product_id"),
                employee_id=data.get("employee_id"),
                user_id=self.user_id,
            )
            
            db.session.execute(stmt)
            db.session.commit()
            return jsonify(
                    {
                        "status_code": 200,
                        "message_id": "success_add_avaliable",
                    }
                ) , 200 
            
            
        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error add avaliable: {e}\n{traceback.format_exc()}",
            )
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "error_processing_add_avaliable",
                        "error": True,
                        "traceback": str(e),
                    }
                ),
                500,
            )
