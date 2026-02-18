from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from src.infrastructure.external_apis.api_base_client import ApiBaseClient

TIMEOUT = 5.0
TIMEOUT_PER_REQUEST = 1.25


@pytest.mark.unit
class TestApiBaseClient:
    @pytest.fixture
    def client(self) -> ApiBaseClient:
        return ApiBaseClient(
            name='TestAPI',
            base_url='https://example.com/',
            timeout=5.0,
            default_headers={'X-Default': '1'},
        )

    @pytest.fixture
    def httpx_client_mocks(self):
        """
        Mocks do httpx.AsyncClient como async context manager.
        Retorna (mock_async_client_cls, mock_client).
        """
        mock_client = AsyncMock()
        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_client
        mock_cm.__aexit__.return_value = None
        return mock_cm, mock_client

    async def test_request_success_merges_headers_and_returns_response(
        self, client, httpx_client_mocks
    ):
        mock_cm, mock_httpx_client = httpx_client_mocks
        response = MagicMock()
        response.raise_for_status = MagicMock()
        mock_httpx_client.request.return_value = response

        with patch(
            'src.infrastructure.external_apis.api_base_client.httpx.AsyncClient',
            return_value=mock_cm,
        ) as mock_async_client_cls:
            result = await client.request({
                'method': 'GET',
                'url': '/health',
                'headers': {'X-Req': '2'},
            })

        assert result is response
        response.raise_for_status.assert_called_once()
        mock_httpx_client.request.assert_awaited_once_with(
            method='GET', url='/health', json=None
        )
        mock_async_client_cls.assert_called_once_with(
            base_url='https://example.com',
            timeout=5.0,
            headers={'X-Default': '1', 'X-Req': '2'},
        )

    async def test_request_uses_per_request_timeout(self, client, httpx_client_mocks):
        mock_cm, mock_httpx_client = httpx_client_mocks
        response = MagicMock()
        response.raise_for_status = MagicMock()
        mock_httpx_client.request.return_value = response

        with patch(
            'src.infrastructure.external_apis.api_base_client.httpx.AsyncClient',
            return_value=mock_cm,
        ) as mock_async_client_cls:
            await client.request({
                'method': 'POST',
                'url': '/x',
                'json': {'a': 1},
                'timeout': TIMEOUT_PER_REQUEST,
            })

        mock_async_client_cls.assert_called_once()
        kwargs = mock_async_client_cls.call_args.kwargs
        assert kwargs['timeout'] == TIMEOUT_PER_REQUEST

    async def test_request_timeout_exception_rewritten(
        self, client, httpx_client_mocks
    ):
        mock_cm, mock_httpx_client = httpx_client_mocks
        mock_httpx_client.request.side_effect = httpx.TimeoutException('orig')

        with patch(
            'src.infrastructure.external_apis.api_base_client.httpx.AsyncClient',
            return_value=mock_cm,
        ):
            with pytest.raises(
                httpx.TimeoutException, match='Request to TestAPI timed out'
            ):
                await client.request({'method': 'GET', 'url': '/x'})

    async def test_request_connect_error_rewritten(self, client, httpx_client_mocks):
        mock_cm, mock_httpx_client = httpx_client_mocks
        mock_httpx_client.request.side_effect = httpx.ConnectError('orig')

        with patch(
            'src.infrastructure.external_apis.api_base_client.httpx.AsyncClient',
            return_value=mock_cm,
        ):
            with pytest.raises(
                httpx.ConnectError, match='Connection to TestAPI failed'
            ):
                await client.request({'method': 'GET', 'url': '/x'})

    async def test_request_http_status_error_rewritten(
        self, client, httpx_client_mocks
    ):
        mock_cm, mock_httpx_client = httpx_client_mocks
        req = httpx.Request('GET', 'https://example.com/x')
        resp = httpx.Response(400, request=req)
        response = MagicMock()
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            'orig', request=req, response=resp
        )
        mock_httpx_client.request.return_value = response

        with patch(
            'src.infrastructure.external_apis.api_base_client.httpx.AsyncClient',
            return_value=mock_cm,
        ):
            with pytest.raises(httpx.HTTPStatusError) as exc_info:
                await client.request({'method': 'GET', 'url': '/x'})

        assert str(exc_info.value) == client.errors.http
        assert exc_info.value.request == req
        assert exc_info.value.response == resp

    async def test_request_request_error_rewritten(self, client, httpx_client_mocks):
        mock_cm, mock_httpx_client = httpx_client_mocks
        req = httpx.Request('GET', 'https://example.com/x')
        mock_httpx_client.request.side_effect = httpx.RequestError('orig', request=req)

        with patch(
            'src.infrastructure.external_apis.api_base_client.httpx.AsyncClient',
            return_value=mock_cm,
        ):
            with pytest.raises(
                httpx.RequestError, match='HTTP error when calling TestAPI'
            ):
                await client.request({'method': 'GET', 'url': '/x'})

    async def test_request_unknown_exception_wrapped(self, client, httpx_client_mocks):
        mock_cm, mock_httpx_client = httpx_client_mocks
        mock_httpx_client.request.side_effect = RuntimeError('boom')

        with patch(
            'src.infrastructure.external_apis.api_base_client.httpx.AsyncClient',
            return_value=mock_cm,
        ):
            with pytest.raises(
                RuntimeError, match='Unknown error when calling TestAPI'
            ):
                await client.request({'method': 'GET', 'url': '/x'})
