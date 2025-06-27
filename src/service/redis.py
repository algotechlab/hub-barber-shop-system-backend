# src/service/redis.py

import os

import redis

HOST_REDIS = os.getenv("HOST_REDIS")
PORT_REDIS = os.getenv("PORT_REDIS")
DB_REDIS = os.getenv("DB_REDIS")
SOCKE_CONNECT_TIMEOUT = os.getenv("SOCKET_CONNECT_TIMEOUT")


class SessionManager:
    def __init__(self):
        self.client = redis.Redis(
            host="localhost",
            port=6379,
            db=0,
            decode_responses=True,
            socket_connect_timeout=5,
        )

    def get(self, phone: str) -> str | None:
        return self.client.get(f"session:{phone}")

    def set(self, phone: str, state: str, expire_seconds: int = 600) -> None:
        self.client.set(f"session:{phone}", state, ex=expire_seconds)

    def clear(self, phone: str) -> None:
        self.client.delete(f"session:{phone}")

    def reset_to_default(self, key: str, RESPONSE_DICTIONARY: dict) -> str:
        self.clear(key)
        return RESPONSE_DICTIONARY["default"]

    def clear_all(self) -> None:
        """Clear all session, message deduplication, and rate limiting keys."""
        for pattern in ["session:*", "msg:*", "rate:*"]:
            cursor = "0"
            while cursor != 0:
                cursor, keys = self.client.scan(
                    cursor=cursor, match=pattern, count=100
                )
                if keys:
                    self.client.delete(*keys)

    def delete(self, key: str) -> None:
        self.client.delete(key)
