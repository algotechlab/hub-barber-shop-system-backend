# src/resource/subscription.py


from flask import jsonify, request
from flask_cors import cross_origin
from flask_restx import Namespace, Resource, fields, reqparse

from src.core.subscription import SubscriptionCore

pagination_arguments_subscription = reqparse.RequestParser()
pagination_arguments_subscription.add_argument(
    "current_page", help="Current Page", default=1, type=int, required=False
)
pagination_arguments_subscription.add_argument(
    "rows_per_page", help="Rows per Page", default=10, type=int, required=False
)
pagination_arguments_subscription.add_argument(
    "order_by", help="Order By", default="", type=str, required=False
)
pagination_arguments_subscription.add_argument(
    "sort_by", help="Sort By", default="", type=str, required=False
)
pagination_arguments_subscription.add_argument(
    "filter_by", help="Filter By", default="", type=str, required=False
)

subscription_ns = Namespace("subscription", description="Manager subscription")


payload_add_subscription = subscription_ns.model(
    "SubscriptionAddPayload",
    {
        "name": fields.String(required=True, description="Name of the subscription"),
        "price": fields.String(required=True, description="Price of the subscription"),
        "days_to_spend": fields.String(
            required=True,
            description="Time duration (e.g. '30 days', '1 month 15 days')",
        ),
        "benefits": fields.String(required=True, description="Description of benefits"),
    },
)

payload_add_users_subscription = subscription_ns.model(
    "SubscriptionUserAddPayload",
    {
        "subscription_id": fields.Integer(required=True, description="Subscription ID"),
        "user_id": fields.Integer(required=True, description="User ID"),
    },
)

payload_update_subscription = subscription_ns.model(
    "SubscriptionUpdatePayload",
    {
        "name": fields.String(required=False, description="Name of the subscription"),
        "price": fields.String(required=False, description="Price of the subscription"),
        "days_to_spend": fields.String(
            required=False,
            description="Time duration (e.g. '30 days', '1 month 15 days')",
        ),
        "benefits": fields.String(
            required=False, description="Description of benefits"
        ),
    },
)


@subscription_ns.route("")
class SubcriptionResource(Resource):
    @subscription_ns.doc(description="Add subscription")
    @subscription_ns.expect(payload_add_subscription, validate=True)
    @cross_origin()
    def post(self):
        """Add subscription"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return SubscriptionCore(user_id=user_id).add_subscription(
                request.get_json()
            )
        except Exception:
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "something_went_wrong",
                        "error": True,
                    },
                )
            ), 500

    @subscription_ns.doc(description="List subscriptions")
    @subscription_ns.expect(pagination_arguments_subscription, validate=True)
    @cross_origin()
    def get(self):
        """List subscriptions"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return SubscriptionCore(user_id=user_id).list_subscription(
                request.args.to_dict()
            )
        except Exception:
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "something_went_wrong",
                        "error": True,
                    },
                )
            ), 500


@subscription_ns.route("/<int:id>")
class SubscriptionResourceID(Resource):
    @subscription_ns.doc(description="Update subscription")
    @subscription_ns.expect(payload_update_subscription, validate=True)
    @cross_origin()
    def put(self, id: int):
        """Update subscription by id"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return SubscriptionCore(user_id=user_id).update_subscription(
                id=id, data=request.get_json()
            )
        except Exception:
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "something_went_wrong",
                        "error": True,
                    },
                )
            ), 500

    @subscription_ns.doc(description="Delete subscription")
    @cross_origin()
    def delete(self, id: int):
        """Delete subscription by id"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return SubscriptionCore(user_id=user_id).delete_subcription(
                id=id,
            )
        except Exception:
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "something_went_wrong",
                        "error": True,
                    },
                )
            ), 500


@subscription_ns.route("/users")
class SubscriptionsUsersResource(Resource):
    @subscription_ns.doc(description="Add subscription users")
    @subscription_ns.expect(payload_add_users_subscription, validate=True)
    @cross_origin()
    def post(self):
        """Add subscription users"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return SubscriptionCore(user_id=user_id).add_user_subscription(
                request.get_json()
            )
        except Exception:
            return (
                jsonify(
                    {
                        "status_code": 500,
                        "message_id": "something_went_wrong",
                        "error": True,
                    },
                )
            ), 500
