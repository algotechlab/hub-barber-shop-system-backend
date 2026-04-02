import json
from http import HTTPStatus
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from src.infrastructure.external_apis.evolution_api import (
    EvolutionApi,
    EvolutionApiNotConfiguredError,
)


def _settings(url: str = 'http://evo.test', key: str = 'secret'):
    s = MagicMock()
    s.EVOLUTION_API_BASE_URL = url
    s.EVOLUTION_API_KEY = key
    s.AUTHENTICATION_API_KEY = ''
    return s


@pytest.mark.unit
class TestEvolutionApi:
    @patch(
        'src.infrastructure.external_apis.evolution_api.get_settings',
        return_value=_settings(),
    )
    def test_is_configured_true(self, mock_get_settings):
        assert mock_get_settings is not None
        api = EvolutionApi()
        assert api.is_configured() is True

    @patch(
        'src.infrastructure.external_apis.evolution_api.get_settings',
        return_value=_settings(url='', key='k'),
    )
    def test_is_configured_false_without_url(self, mock_get_settings):
        assert mock_get_settings is not None
        api = EvolutionApi()
        assert api.is_configured() is False

    @patch(
        'src.infrastructure.external_apis.evolution_api.get_settings',
        return_value=_settings(url='http://x', key=''),
    )
    def test_is_configured_false_without_key(self, mock_get_settings):
        assert mock_get_settings is not None
        api = EvolutionApi()
        assert api.is_configured() is False

    @patch.object(EvolutionApi, 'request', new_callable=AsyncMock)
    @patch(
        'src.infrastructure.external_apis.evolution_api.get_settings',
        return_value=_settings(),
    )
    async def test_get_connection_state_raw(self, mock_get_settings, mock_request):
        assert mock_get_settings is not None
        mock_request.return_value = httpx.Response(HTTPStatus.OK, json={})
        api = EvolutionApi()
        r = await api.get_connection_state_raw('inst-1')
        assert r.status_code == HTTPStatus.OK
        mock_request.assert_awaited()
        call = mock_request.await_args[0][0]
        assert call['method'] == 'GET'
        assert 'connectionState' in call['url']

    @patch(
        'src.infrastructure.external_apis.evolution_api.get_settings',
        return_value=_settings(url='', key=''),
    )
    async def test_get_connection_state_raises_when_not_configured(
        self, mock_get_settings
    ):
        assert mock_get_settings is not None
        api = EvolutionApi()
        with pytest.raises(EvolutionApiNotConfiguredError):
            await api.get_connection_state_raw('x')

    @patch.object(EvolutionApi, 'request', new_callable=AsyncMock)
    @patch(
        'src.infrastructure.external_apis.evolution_api.get_settings',
        return_value=_settings(),
    )
    async def test_create_instance_ok_and_created(
        self, mock_get_settings, mock_request
    ):
        assert mock_get_settings is not None
        api = EvolutionApi()
        for code in (HTTPStatus.OK, HTTPStatus.CREATED):
            resp = MagicMock()
            resp.status_code = code
            resp.json.return_value = {'ok': True}
            mock_request.return_value = resp
            out = await api.create_instance('n')
            assert out == {'ok': True}

    @patch.object(EvolutionApi, 'request', new_callable=AsyncMock)
    @patch(
        'src.infrastructure.external_apis.evolution_api.get_settings',
        return_value=_settings(),
    )
    async def test_create_instance_forbidden_with_json(
        self, mock_get_settings, mock_request
    ):
        assert mock_get_settings is not None
        resp = MagicMock()
        resp.status_code = HTTPStatus.FORBIDDEN
        resp.json.return_value = {'exists': True}
        mock_request.return_value = resp
        api = EvolutionApi()
        assert await api.create_instance('dup') == {'exists': True}

    @patch.object(EvolutionApi, 'request', new_callable=AsyncMock)
    @patch(
        'src.infrastructure.external_apis.evolution_api.get_settings',
        return_value=_settings(),
    )
    async def test_create_instance_forbidden_bad_json(
        self, mock_get_settings, mock_request
    ):
        assert mock_get_settings is not None
        resp = MagicMock()
        resp.status_code = HTTPStatus.FORBIDDEN
        resp.json.side_effect = json.JSONDecodeError('x', '', 0)
        mock_request.return_value = resp
        api = EvolutionApi()
        assert await api.create_instance('dup') == {}

    @patch.object(EvolutionApi, 'request', new_callable=AsyncMock)
    @patch(
        'src.infrastructure.external_apis.evolution_api.get_settings',
        return_value=_settings(),
    )
    async def test_create_instance_other_status_raises(
        self, mock_get_settings, mock_request
    ):
        assert mock_get_settings is not None
        req = httpx.Request('POST', 'https://x')
        resp = httpx.Response(HTTPStatus.INTERNAL_SERVER_ERROR, request=req)
        mock_request.return_value = resp
        api = EvolutionApi()
        with pytest.raises(httpx.HTTPStatusError):
            await api.create_instance('x')

    @patch.object(EvolutionApi, 'request', new_callable=AsyncMock)
    @patch(
        'src.infrastructure.external_apis.evolution_api.get_settings',
        return_value=_settings(),
    )
    async def test_create_instance_other_status_no_raise_returns_json(
        self, mock_get_settings, mock_request
    ):
        assert mock_get_settings is not None
        resp = MagicMock()
        resp.status_code = HTTPStatus.BAD_REQUEST
        resp.raise_for_status = MagicMock()
        resp.json.return_value = {'detail': 'ok'}
        mock_request.return_value = resp
        api = EvolutionApi()
        assert await api.create_instance('x') == {'detail': 'ok'}

    @patch.object(EvolutionApi, 'request', new_callable=AsyncMock)
    @patch(
        'src.infrastructure.external_apis.evolution_api.get_settings',
        return_value=_settings(),
    )
    async def test_get_connect_raw(self, mock_get_settings, mock_request):
        assert mock_get_settings is not None
        mock_request.return_value = httpx.Response(HTTPStatus.OK)
        api = EvolutionApi()
        r = await api.get_connect_raw('i')
        assert r.status_code == HTTPStatus.OK

    @patch.object(EvolutionApi, 'request', new_callable=AsyncMock)
    @patch(
        'src.infrastructure.external_apis.evolution_api.get_settings',
        return_value=_settings(),
    )
    async def test_send_text(self, mock_get_settings, mock_request):
        assert mock_get_settings is not None
        mock_request.return_value = httpx.Response(
            HTTPStatus.OK,
            json={'sent': True},
        )
        api = EvolutionApi()
        out = await api.send_text('inst', number='5511', text='hi')
        assert out == {'sent': True}

    def test_auth_falls_back_to_authentication_api_key(self):
        s = _settings(key='')
        s.AUTHENTICATION_API_KEY = 'fallback'
        with patch(
            'src.infrastructure.external_apis.evolution_api.get_settings',
            return_value=s,
        ):
            api = EvolutionApi()
            assert api._api_key() == 'fallback'

    @patch(
        'src.infrastructure.external_apis.evolution_api.get_settings',
        return_value=_settings(),
    )
    def test_safe_instance_path_encodes(self, mock_get_settings):
        assert mock_get_settings is not None
        api = EvolutionApi()
        assert ' ' not in api._safe_instance_path('a b')
