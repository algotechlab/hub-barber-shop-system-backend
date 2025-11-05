import hashlib


class CompactHash:

    @staticmethod
    def compact_token(token: str) -> str:
        """Generate a compact hash for the given token."""
        return hashlib.sha256(token.encode()).hexdigest()[:16]
