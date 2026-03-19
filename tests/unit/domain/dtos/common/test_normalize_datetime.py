from datetime import datetime, timezone

import pytest
from src.domain.dtos.common.normalize_datetime import normalize_datetime_to_naive_utc

pytestmark = pytest.mark.unit


def test_normalize_returns_none_when_value_is_none():
    assert normalize_datetime_to_naive_utc(None) is None


def test_normalize_strips_utc_tzinfo():
    value = datetime(2026, 2, 14, 20, 6, 18, tzinfo=timezone.utc)
    out = normalize_datetime_to_naive_utc(value)
    assert out.tzinfo is None
    assert out == datetime(2026, 2, 14, 20, 6, 18)


def test_normalize_returns_naive_unchanged():
    naive = datetime(2026, 2, 14, 20, 6, 18)
    assert normalize_datetime_to_naive_utc(naive) is naive
