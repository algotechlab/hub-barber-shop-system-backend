from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from src.core.config.settings import get_settings


def create_owner_access_token(owner_id: UUID) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {
        'sub': str(owner_id),
        'iat': int(now.timestamp()),
        'exp': int(expires_at.timestamp()),
    }
    return jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
