from http import HTTPStatus
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import httpx
import pytest
from src.core.exceptions.custom import DomainException
from src.domain.dtos.marketing import (
    InactiveClientsPayloadDTO,
    MessageTemplateDTO,
    TemplateMarketingRecordDTO,
)
from src.domain.service import marketing as marketing_mod
from src.domain.service.marketing import MarketingService
from src.infrastructure.external_apis.evolution_api import (
    EvolutionApiNotConfiguredError,
)


def _evolution_mock(
    *,
    configured: bool = True,
) -> MagicMock:
    ev = MagicMock()
    ev.is_configured = MagicMock(return_value=configured)
    ev.get_connection_state_raw = AsyncMock()
    ev.get_connect_raw = AsyncMock()
    ev.create_instance = AsyncMock()
    ev.send_text = AsyncMock()
    return ev


@pytest.mark.unit
class TestMarketingHelpers:
    def test_template_text_from_context_empty_and_fallbacks(self):
        assert marketing_mod._template_text_from_context({}) == ''
        assert marketing_mod._template_text_from_context({'template': 'a'}) == 'a'
        assert marketing_mod._template_text_from_context({'body': 'b'}) == 'b'
        assert marketing_mod._template_text_from_context({'message': 'm'}) == 'm'

    def test_map_evolution_state(self):
        assert marketing_mod._map_evolution_state('') == 'unknown'
        assert marketing_mod._map_evolution_state('open') == 'open'
        assert marketing_mod._map_evolution_state('CONNECTING') == 'connecting'
        assert marketing_mod._map_evolution_state('qr') == 'connecting'
        assert marketing_mod._map_evolution_state('pairing') == 'connecting'
        assert marketing_mod._map_evolution_state('connected') == 'open'
        assert marketing_mod._map_evolution_state('closed') == 'close'

    def test_extract_qr_base64(self):
        assert marketing_mod._extract_qr_base64({}) is None
        assert (
            marketing_mod._extract_qr_base64({'qrcode': {'base64': '  abc  '}}) == 'abc'
        )
        assert marketing_mod._extract_qr_base64({'qrcode': {'code': 'x'}}) == 'x'
        assert marketing_mod._extract_qr_base64({'base64': 'y'}) == 'y'
        assert marketing_mod._extract_qr_base64({'code': 'z'}) == 'z'

    def test_whatsapp_state_from_mapping(self):
        assert marketing_mod._whatsapp_state_from_mapping('connecting', '', None) == (
            'connecting'
        )
        assert marketing_mod._whatsapp_state_from_mapping('close', 'x', None) == (
            'close'
        )
        assert marketing_mod._whatsapp_state_from_mapping('unknown', '', 'qr') == (
            'connecting'
        )

    def test_evolution_http_message_branches(self):
        req = httpx.Request('GET', 'https://x')
        resp = httpx.Response(
            400,
            request=req,
            json={'response': {'message': ['first']}},
        )
        exc = httpx.HTTPStatusError('x', request=req, response=resp)
        assert marketing_mod._evolution_http_message(exc) == 'first'

        resp2 = httpx.Response(
            400, request=req, json={'response': {'message': 'plain'}}
        )
        exc2 = httpx.HTTPStatusError('x', request=req, response=resp2)
        assert marketing_mod._evolution_http_message(exc2) == 'plain'

        resp3 = httpx.Response(400, request=req, json={'error': 'e'})
        exc3 = httpx.HTTPStatusError('x', request=req, response=resp3)
        assert marketing_mod._evolution_http_message(exc3) == 'e'

        resp4 = httpx.Response(400, request=req, content=b'not-valid-json{{{')
        exc4 = httpx.HTTPStatusError('x', request=req, response=resp4)
        assert marketing_mod._evolution_http_message(exc4) == str(exc4)

        resp5 = httpx.Response(400, request=req, content=b'not-json{{{')
        exc5 = httpx.HTTPStatusError('x', request=req, response=resp5)
        out = marketing_mod._evolution_http_message(exc5)
        assert isinstance(out, str)
        assert len(out) > 0

        resp6 = httpx.Response(400, request=req, json={'other': 'x'})
        exc6 = httpx.HTTPStatusError('x', request=req, response=resp6)
        out6 = marketing_mod._evolution_http_message(exc6)
        assert isinstance(out6, str)
        assert len(out6) > 0


@pytest.mark.unit
class TestMarketingService:
    @pytest.fixture
    def template_repo(self):
        return AsyncMock()

    @pytest.fixture
    def evolution(self):
        return _evolution_mock()

    @pytest.fixture
    def inactive_repo(self):
        return AsyncMock()

    @pytest.fixture
    def service(self, template_repo, evolution, inactive_repo):
        return MarketingService(template_repo, evolution, inactive_repo)

    def test_instance_name_for_company(self, service):
        cid = uuid4()
        assert service.instance_name_for_company(cid) == f'barber-{cid}'

    async def test_get_message_template_empty(self, service, template_repo):
        template_repo.get_active_for_company.return_value = None
        out = await service.get_message_template(uuid4())
        assert out == MessageTemplateDTO(template='')

    async def test_get_message_template_with_row(self, service, template_repo):
        template_repo.get_active_for_company.return_value = TemplateMarketingRecordDTO(
            id=uuid4(),
            company_id=uuid4(),
            name='n',
            description='d',
            context_template={'template': 'hello'},
            is_active=True,
        )
        out = await service.get_message_template(uuid4())
        assert out.template == 'hello'

    async def test_save_message_template(self, service, template_repo):
        cid = uuid4()
        out = await service.save_message_template(cid, 't')
        template_repo.upsert_default_template.assert_awaited_once_with(cid, 't')
        assert out.template == 't'

    async def test_get_whatsapp_connection_not_configured(self, service, evolution):
        evolution.is_configured.return_value = False
        out = await service.get_whatsapp_connection(uuid4())
        assert out.state == 'unknown'
        assert out.qr_base64 is None

    async def test_get_whatsapp_connection_evolution_not_configured_after_start(
        self, service, evolution
    ):
        evolution.is_configured.return_value = True
        evolution.get_connection_state_raw.side_effect = EvolutionApiNotConfiguredError(
            'x'
        )
        out = await service.get_whatsapp_connection(uuid4())
        assert out.state == 'unknown'

    async def test_get_whatsapp_connection_open(self, service, evolution):
        evolution.is_configured.return_value = True
        req = httpx.Request('GET', 'https://x')
        res = httpx.Response(
            HTTPStatus.OK,
            request=req,
            json={'instance': {'state': 'open'}},
        )
        evolution.get_connection_state_raw.return_value = res
        out = await service.get_whatsapp_connection(uuid4())
        assert out.state == 'open'
        assert out.qr_base64 is None

    async def test_get_whatsapp_connection_with_qr(self, service, evolution):
        evolution.is_configured.return_value = True
        req = httpx.Request('GET', 'https://x')
        res = httpx.Response(
            HTTPStatus.OK,
            request=req,
            json={'instance': {'state': 'close'}},
        )
        evolution.get_connection_state_raw.return_value = res
        qr = httpx.Response(
            HTTPStatus.OK,
            request=req,
            json={'base64': 'AAA'},
        )
        evolution.get_connect_raw.return_value = qr
        out = await service.get_whatsapp_connection(uuid4())
        assert out.qr_base64 == 'AAA'
        assert out.state == 'connecting'

    async def test_get_whatsapp_connection_404_creates_instance(
        self, service, evolution
    ):
        evolution.is_configured.return_value = True
        req = httpx.Request('GET', 'https://x')
        first = MagicMock()
        first.status_code = HTTPStatus.NOT_FOUND
        second = httpx.Response(
            HTTPStatus.OK,
            request=req,
            json={'instance': {'state': 'open'}},
        )
        evolution.get_connection_state_raw.side_effect = [first, second]
        evolution.create_instance = AsyncMock(return_value={})
        out = await service.get_whatsapp_connection(uuid4())
        evolution.create_instance.assert_awaited_once()
        assert out.state == 'open'

    async def test_get_whatsapp_connection_http_status_error(self, service, evolution):
        evolution.is_configured.return_value = True
        req = httpx.Request('GET', 'https://x')
        resp = httpx.Response(400, request=req, json={'error': 'bad'})
        resp.raise_for_status = MagicMock(
            side_effect=httpx.HTTPStatusError('x', request=req, response=resp)
        )
        evolution.get_connection_state_raw.return_value = resp
        with pytest.raises(DomainException):
            await service.get_whatsapp_connection(uuid4())

    async def test_get_whatsapp_connection_http_error(self, service, evolution):
        evolution.is_configured.return_value = True
        evolution.get_connection_state_raw.side_effect = httpx.ConnectError('nope')
        with pytest.raises(DomainException, match='indisponível'):
            await service.get_whatsapp_connection(uuid4())

    async def test_get_whatsapp_connection_qr_http_error(self, service, evolution):
        evolution.is_configured.return_value = True
        res = MagicMock()
        res.status_code = HTTPStatus.OK
        res.json.return_value = {'instance': {'state': 'x'}}
        evolution.get_connection_state_raw.return_value = res
        evolution.get_connect_raw.side_effect = httpx.TimeoutException('t')
        with pytest.raises(DomainException):
            await service.get_whatsapp_connection(uuid4())

    async def test_get_whatsapp_connection_qr_http_status_error(
        self, service, evolution
    ):
        evolution.is_configured.return_value = True
        req = httpx.Request('GET', 'https://x')
        state = httpx.Response(
            HTTPStatus.OK,
            request=req,
            json={'instance': {'state': 'close'}},
        )
        evolution.get_connection_state_raw.return_value = state
        bad_qr = httpx.Response(
            HTTPStatus.BAD_REQUEST,
            request=req,
            json={'error': 'qr'},
        )
        evolution.get_connect_raw.return_value = bad_qr
        with pytest.raises(DomainException):
            await service.get_whatsapp_connection(uuid4())

    async def test_get_inactive_clients(self, service, inactive_repo):
        cid = uuid4()
        expected = InactiveClientsPayloadDTO(users=[], schedules=[])
        inactive_repo.fetch_inactive_clients.return_value = expected
        out = await service.get_inactive_clients(
            cid,
            email='a',
            min_days=1,
            max_days=99,
            lookback_years=1,
            schedules_limit=10,
        )
        assert out == expected
        inactive_repo.fetch_inactive_clients.assert_awaited_once_with(
            cid,
            email='a',
            min_days=1,
            max_days=99,
            lookback_years=1,
            schedules_limit=10,
        )

    async def test_send_template_message_with_override(self, service, evolution):
        evolution.is_configured.return_value = True
        await service.send_template_message(uuid4(), '5511', 'direct')
        evolution.send_text.assert_awaited_once()
        call = evolution.send_text.await_args
        assert call.kwargs['text'] == 'direct'

    async def test_send_template_message_uses_saved_template(self, service, evolution):
        evolution.is_configured.return_value = True
        service.get_message_template = AsyncMock(
            return_value=MessageTemplateDTO(template='saved')
        )
        await service.send_template_message(uuid4(), '5511', None)
        assert evolution.send_text.await_args.kwargs['text'] == 'saved'

    async def test_send_template_message_no_template_raises(self, service, evolution):
        evolution.is_configured.return_value = True
        service.get_message_template = AsyncMock(
            return_value=MessageTemplateDTO(template='')
        )
        with pytest.raises(DomainException, match='template'):
            await service.send_template_message(uuid4(), '5511', None)

    async def test_send_not_configured(self, service, evolution):
        evolution.is_configured.return_value = False
        with pytest.raises(DomainException, match='não configurada'):
            await service.send_template_message(uuid4(), '5511', 'texto')

    async def test_send_evolution_not_configured_error(self, service, evolution):
        evolution.is_configured.return_value = True
        evolution.send_text.side_effect = EvolutionApiNotConfiguredError('msg')
        with pytest.raises(DomainException, match='msg'):
            await service.send_template_message(uuid4(), '5511', 'hi')

    async def test_send_http_status_error(self, service, evolution):
        evolution.is_configured.return_value = True
        req = httpx.Request('POST', 'https://x')
        resp = httpx.Response(500, request=req, json={'error': 'e'})
        evolution.send_text.side_effect = httpx.HTTPStatusError(
            'x', request=req, response=resp
        )
        with pytest.raises(DomainException):
            await service.send_template_message(uuid4(), '5511', 'hi')

    async def test_send_http_error(self, service, evolution):
        evolution.is_configured.return_value = True
        evolution.send_text.side_effect = httpx.ConnectError('x')
        with pytest.raises(DomainException, match='indisponível'):
            await service.send_template_message(uuid4(), '5511', 'hi')
