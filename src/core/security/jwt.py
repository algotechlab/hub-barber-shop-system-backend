from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from src.core.config.settings import get_settings


def create_access_token(
    subject_id: UUID,
    token_type: str,
    *,
    company_id: UUID | None = None,
) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {
        'sub': str(subject_id),
        'typ': token_type,
        'iat': int(now.timestamp()),
        'exp': int(expires_at.timestamp()),
    }
    if company_id is not None:
        payload['company_id'] = str(company_id)
    return jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_owner_access_token(owner_id: UUID) -> str:
    return create_access_token(owner_id, 'owner')
