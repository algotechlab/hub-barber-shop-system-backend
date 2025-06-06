
import redis


class SessionManager:
    def __init__(self):
        self.client = redis.Redis(
            host="localhost",
            port=6379,
            db=0,
            decode_responses=True,
        )

    def get(self, phone: str) -> str | None:
        return self.client.get(f"session:{phone}")

    def set(self, phone: str, state: str, expire_seconds: int = 600) -> None:
        self.client.set(f"session:{phone}", state, ex=expire_seconds)

    def clear(self, phone: str) -> None:
        self.client.delete(f"session:{phone}")
