# src/core/subscription.py
import traceback
from datetime import datetime

from flask import jsonify
from sqlalchemy import extract, func, insert, select, update

from src.db.database import db
from src.model.model import Subscription, SubscriptionUser
from src.utils.log import logdb
from src.utils.metadata import Metadata
from src.utils.pagination import Pagination

SUBSCRIPTION_FIELDS = [
    "name",
    "price",
    "days_to_spend",
    "benefits",
]


class SubscriptionCore:
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        self.subscription = Subscription
        self.subscription_user = SubscriptionUser

    def add_subscription(self, data: dict):
        try:
            time_to_spend = data.get("days_to_spend")
            if not isinstance(time_to_spend, str):
                raise ValueError("time_to_spend must be a string (e.g., '30 days')")

            stmt = insert(self.subscription).values(
                name=data.get("name"),
                price=float(data.get("price")),
                days_to_spend=time_to_spend,
                benefits=data.get("benefits"),
            )
            db.session.execute(stmt)
            db.session.commit()
            return (
                jsonify(
                    {
                        "status_code": 200,
                        "message_id": "success_add_subscription",
                        "error": False,
                    }
                ),
                200,
            )

        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error add subscription: \
                {e}\n{traceback.format_exc()}",
            )
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "something_went_wrong",
                        "error": True,
                        "exception": str(e),
                        "traceback": traceback.format_exc(),
                    }
                ),
                500,
            )

    def add_user_subscription(self, data: dict):
        try:
            start_subscription = datetime.utcnow()
            stmt = insert(self.subscription_user).values(
                subscription_id=data.get("subscription_id"),
                user_id=data.get("user_id"),
                start_subscription=start_subscription,
            )
            db.session.execute(stmt)
            db.session.commit()
            return (
                jsonify(
                    {
                        "status_code": 200,
                        "message_id": "success_add_user_subscription",
                        "error": False,
                    }
                ),
                200,
            )

        except Exception as e:
            print(f"Error add user subscription: {e}")
            db.session.rollback()
            logdb(
                "error",
                message=f"Error add user subscription: \
                {e}\n{traceback.format_exc()}",
            )
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "something_went_wrong",
                        "error": True,
                        "exception": str(e),
                        "traceback": traceback.format_exc(),
                    }
                ),
                500,
            )

    def list_subscription(self, data: dict):
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
                self.subscription.id,
                self.subscription.name,
                self.subscription.price,
                extract("day", self.subscription.days_to_spend).label("days_to_spend"),
                self.subscription.benefits,
            ).where(~self.subscription.is_deleted)

            if pagination_params.filter_by:
                filter_value = f"%{pagination_params.filter_by}%"
                try:
                    stmt = stmt.filter(
                        func.unaccent(self.subscription.name).ilike(
                            func.unaccent(filter_value)
                        )
                    )
                except Exception:
                    stmt = stmt.filter(self.subscription.name.ilike(filter_value))

            sort_column = getattr(self.subscription, pagination_params.order_by, None)
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
                (pagination_params.current_page - 1) * pagination_params.rows_per_page
            ).limit(pagination_params.rows_per_page)

            # Executa a consulta
            result = db.session.execute(paginated_stmt).fetchall()

            if not result:
                return jsonify(
                    {
                        "status_code": 404,
                        "message_id": "subscription_not_found",
                    }
                )

            metadata = pagination.build_metadata(total_count, pagination_params)

            return jsonify(
                {
                    "status_code": 200,
                    "data": Metadata(result).model_to_list(),
                    "metadata": metadata if metadata else {},
                    "message_id": "list_success_subscription",
                }
            )

        except Exception as e:
            print("Coletando o error", e)
            logdb(
                "error",
                message=f"Error listing users: \
                {e}\n{traceback.format_exc()}",
            )
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "error_processing_list_subscription",
                    }
                ),
                500,
            )

    def update_subscription(self, id: int, data: dict):
        try:
            subscription = self.subscription.query.filter_by(id=id).first()

            if not subscription:
                return jsonify(
                    {
                        "status_code": 404,
                        "message_id": "subscription_not_found",
                    }
                )

            update_data = {}
            for key, value in data.items():
                if value is not None and key in SUBSCRIPTION_FIELDS:
                    if hasattr(subscription, key):
                        setattr(subscription, key, value)
                        update_data[key] = value

            stmt = (
                update(self.subscription)
                .where(self.subscription.id == id)
                .values(
                    **update_data,
                    updated_at=datetime.utcnow(),
                    updated_by=self.user_id,
                )
            )

            db.session.execute(stmt)
            db.session.commit()

            return (
                jsonify(
                    {
                        "status_code": 200,
                        "message_id": "success_update_subscription",
                        "error": False,
                    }
                ),
                200,
            )

        except Exception as e:
            logdb(
                "error",
                message=f"Error update subscription: \
                {e}\n{traceback.format_exc()}",
            )
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "something_went_wrong",
                        "error": True,
                        "exception": str(e),
                        "traceback": traceback.format_exc(),
                    }
                ),
                500,
            )

    def delete_subcription(self, id: int):
        try:
            stmt = (
                update(self.subscription)
                .where(self.subscription.id == id)
                .values(
                    is_deleted=True,
                    deleted_by=self.user_id,
                    deleted_at=datetime.utcnow(),
                )
            )
            db.session.execute(stmt)
            db.session.commit()
            return (
                jsonify(
                    {
                        "status_code": 200,
                        "message_id": "success_delete_subscription",
                        "error": False,
                    }
                ),
                200,
            )
        except Exception as e:
            db.session.rollback()
            logdb(
                "error",
                message=f"Error delete subscription: \
                {e}\n{traceback.format_exc()}",
            )
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "something_went_wrong",
                        "error": True,
                        "exception": str(e),
                        "traceback": traceback.format_exc(),
                    }
                ),
                500,
            )
