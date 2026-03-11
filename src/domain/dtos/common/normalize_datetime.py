from datetime import datetime, timezone
from typing import Optional


def normalize_datetime_to_naive_utc(value: Optional[datetime]) -> Optional[datetime]:
    """
    Converte datetime timezone-aware
    para UTC sem tzinfo (Postgres TIMESTAMP WITHOUT TIME ZONE).
    """
    if value is None:
        return None
    if isinstance(value, datetime) and value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value
