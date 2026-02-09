from unittest.mock import MagicMock

import pytest
from fastapi import Request
from src.core.exceptions.custom import (
    DomainException,
    InfrastructureException,
    MultipleException,
)
from src.interface.api.v1.middlewares.exceptions import custom_exception_handler


@pytest.mark.unit
class TestCustomExceptionHandler:
    @pytest.fixture
    def request_mock(self):
        return MagicMock(spec=Request)

    async def test_domain_exception_returns_400(self, request_mock):
        status_code = 400
        exc = DomainException('Erro de domínio')
        response = await custom_exception_handler(request_mock, exc)
        assert response.status_code == status_code
        body = response.body.decode()
        assert 'DOMAIN_ERROR' in body or 'message' in body

    async def test_infrastructure_exception_returns_500(self, request_mock):
        status_code = 500
        exc = InfrastructureException('Erro interno')
        response = await custom_exception_handler(request_mock, exc)
        assert response.status_code == status_code
        body = response.body.decode()
        assert 'INTERNAL_ERROR' in body or 'message' in body

    async def test_multiple_exception_returns_errors_list(self, request_mock):
        status_code = 400
        err1 = DomainException('Erro 1')
        err2 = DomainException('Erro 2')
        exc = MultipleException(err1, err2)
        response = await custom_exception_handler(request_mock, exc)
        assert response.status_code == status_code
        import json

        content = json.loads(response.body.decode())
        assert isinstance(content, list)
        assert len(content) >= 1

    async def test_generic_exception_returns_500(self, request_mock):
        status_code = 500
        exc = ValueError('Qualquer erro')
        response = await custom_exception_handler(request_mock, exc)
        assert response.status_code == status_code
