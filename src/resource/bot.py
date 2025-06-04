from flask import jsonify, request
from flask_cors import cross_origin
from flask_restx import Namespace, Resource, fields
from src.core.bot import BotCore

webhook_ns = Namespace("webhook", description="Manager webhook")

payload_webhook = webhook_ns.model(
    "WebhookPayload",
    {
        "type": fields.String(description="Type of message"),
        "from": fields.String(description="Sender phone number"),
        "textMessage": fields.Nested(
            webhook_ns.model(
                "TextMessage",
                {
                    "text": fields.String(description="Message text"),
                }
            ),
            required=False,
        ),
        "text": fields.String(description="Fallback text field", required=False),
    },
)

@webhook_ns.route("/messages-upsert")
class Webhook(Resource):
    @webhook_ns.expect(payload_webhook)
    @cross_origin()
    def post(self):
        data = request.get_json()
        print("parametro vindo do data", data)
        message = data['data']['message']['conversation']
        sender_number = data['data']['key']['remoteJid'].split("@")[0]
        BotCore().send_message(message=message, sender_number=sender_number)
        return jsonify({"response": message})

@webhook_ns.route('/health')
class HealthCheck(Resource):
    @cross_origin()
    def get(self):
        """Verifica se o servidor está funcionando"""
        return {"message": "Webhook do WhatsApp Bot está funcionando!"}, 200