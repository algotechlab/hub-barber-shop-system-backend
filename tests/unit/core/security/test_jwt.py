from unittest.mock import MagicMock, patch
from uuid import uuid4

import jwt
import pytest
from src.core.security.jwt import create_owner_access_token

pytestmark = pytest.mark.unit


def test_create_owner_access_token_contains_expected_claims():
    owner_id = uuid4()
    settings = MagicMock(
        JWT_EXPIRE_MINUTES=60, JWT_SECRET='secret', JWT_ALGORITHM='HS256'
    )

    with patch('src.core.security.jwt.get_settings', return_value=settings):
        token = create_owner_access_token(owner_id)

    payload = jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
    )
    assert payload['sub'] == str(owner_id)
    assert 'iat' in payload
    assert 'exp' in payload
