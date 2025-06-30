from flask import request
from flask_cors import cross_origin
from flask_restx import Namespace, Resource, fields

from src.bot.core import BotCore
from src.service.redis import SessionManager
from src.utils.log import logdb

webhook_ns = Namespace("webhook", description="Manager webhook")

RATE_COUNT_LIMIT_MESSAGE = 15

payload_webhook = webhook_ns.model(
    "WebhookPayload",
    {
        "event": fields.String(description="Event type"),
        "instance": fields.String(description="Instance name"),
        "data": fields.Nested(
            webhook_ns.model(
                "Data",
                {
                    "key": fields.Nested(
                        webhook_ns.model(
                            "Key",
                            {
                                "remoteJid": fields.String(
                                    description="Sender phone"
                                ),
                                "fromMe": fields.Boolean(
                                    description="Message from bot"
                                ),
                                "id": fields.String(description="Message ID"),
                            },
                        )
                    ),
                    "pushName": fields.String(
                        description="Sender's push name"
                    ),
                    "status": fields.String(description="Message status"),
                    "message": fields.Nested(
                        webhook_ns.model(
                            "Message",
                            {
                                "conversation": fields.String(required=False),
                                "extendedTextMessage": fields.Nested(
                                    webhook_ns.model(
                                        "ExtendedTextMessage",
                                        {
                                            "text": fields.String(
                                                required=False
                                            ),
                                        },
                                    ),
                                    required=False,
                                ),
                            },
                        )
                    ),
                    "messageType": fields.String(description="Message type"),
                    "messageTimestamp": fields.Integer(
                        description="Timestamp"
                    ),
                    "instanceId": fields.String(description="Instance ID"),
                    "source": fields.String(description="Source device"),
                },
            )
        ),
        "destination": fields.String(description="Webhook destination"),
        "date_time": fields.String(description="Event timestamp"),
        "sender": fields.String(description="Sender phone"),
        "server_url": fields.String(description="Server URL"),
        "apikey": fields.String(description="API key"),
    },
)


@webhook_ns.route("")
class Webhook(Resource):
    @webhook_ns.expect(payload_webhook)
    @cross_origin()
    def post(self):
        data = request.get_json()
        session = SessionManager()

        if not data or "data" not in data:
            logdb("error", message="No payload received")
            return {"status": "error", "message": "No payload received"}, 400

        try:
            payload_data = data["data"]
            logdb("debug", message=f"Received payload: {payload_data}")
            # Ignorar mensagens enviadas pelo bot
            if payload_data.get("key", {}).get("fromMe", False):
                logdb(
                    "info", message="Ignoring message from bot (fromMe: True)"
                )
                return {
                    "status": "ignored",
                    "message": "Message from bot",
                }, 200

            # Extrai número de telefone, ID da mensagem e timestamp
            phone_number = (
                payload_data.get("key", {}).get("remoteJid", "").split("@")[0]
            )
            message_id = payload_data.get("key", {}).get("id", "")
            message_timestamp = payload_data.get("messageTimestamp", 0)
            push_name = payload_data.get("pushName", "Usuário")
            message_data = payload_data.get("message", {})

            if not phone_number or not message_id or not message_timestamp:
                logdb(
                    "error",
                    message=f"Missing phone number, message ID, or timestamp: from={phone_number}, id={message_id}, timestamp={message_timestamp}",
                )
                return {
                    "status": "error",
                    "message": "Missing required fields",
                }, 400

            # Deduplicação: verifica se mensagem já foi processada
            dedup_key = f"msg:{phone_number}:{message_id}:{message_timestamp}"
            if session.client.get(dedup_key):
                logdb(
                    "info",
                    message=f"Duplicate message ignored: {message_id}, timestamp: {message_timestamp}",
                )
                return {
                    "status": "ignored",
                    "message": "Duplicate message",
                }, 200
            session.client.set(
                dedup_key, "processed", ex=600
            )  # Expira em 10 minutos

            # Rate limiting: limita mensagens por número
            rate_key = f"rate:{phone_number}"
            rate_count = session.client.incr(rate_key)
            if rate_count == 1:
                session.client.expire(rate_key, 60)  # Expira em 1 minuto
            if rate_count > RATE_COUNT_LIMIT_MESSAGE:
                logdb(
                    "warning",
                    message=f"Rate limit exceeded for {phone_number}",
                )
                return {"status": "error", "message": "Too many requests"}, 429

            # Extrai texto da mensagem
            message_text = (
                message_data.get("conversation")
                or message_data.get("extendedTextMessage", {}).get("text")
                or ""
            )
            message_text = message_text.strip().lower()

            if not message_text:
                logdb(
                    "error",
                    message=f"No message text found: from={phone_number}",
                )
                return {"status": "error", "message": "No message text"}, 400

            BotCore(message_text, phone_number, push_name).send_message()
            return {"status": "success"}, 200

        except Exception as e:
            print("coletnado o erro 500", e)
            logdb("error", message=f"Error processing webhook: {str(e)}")
            return {
                "status": "error",
                "message": "Error processing webhook",
            }, 500


@webhook_ns.route("/health")
class HealthCheck(Resource):
    @cross_origin()
    def get(self):
        return {"message": "Webhook do WhatsApp Bot está funcionando!"}, 200
