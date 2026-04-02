from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.domain.dtos.marketing import (
    InactiveClientsPayloadDTO,
    MessageTemplateDTO,
    WhatsappConnectionDTO,
)
from src.domain.use_case.marketing import MarketingUseCase


@pytest.mark.unit
class TestMarketingUseCase:
    @pytest.fixture
    def mock_service(self):
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_service):
        return MarketingUseCase(mock_service)

    async def test_get_message_template(self, use_case, mock_service):
        expected = MessageTemplateDTO(template='x')
        mock_service.get_message_template.return_value = expected
        cid = uuid4()
        assert await use_case.get_message_template(cid) == expected
        mock_service.get_message_template.assert_awaited_once_with(cid)

    async def test_save_message_template(self, use_case, mock_service):
        expected = MessageTemplateDTO(template='y')
        mock_service.save_message_template.return_value = expected
        cid = uuid4()
        assert await use_case.save_message_template(cid, 'y') == expected
        mock_service.save_message_template.assert_awaited_once_with(cid, 'y')

    async def test_get_whatsapp_connection(self, use_case, mock_service):
        expected = WhatsappConnectionDTO(state='open', qr_base64=None)
        mock_service.get_whatsapp_connection.return_value = expected
        cid = uuid4()
        assert await use_case.get_whatsapp_connection(cid) == expected
        mock_service.get_whatsapp_connection.assert_awaited_once_with(cid)

    async def test_get_inactive_clients(self, use_case, mock_service):
        expected = InactiveClientsPayloadDTO(users=[], schedules=[])
        mock_service.get_inactive_clients.return_value = expected
        cid = uuid4()
        out = await use_case.get_inactive_clients(
            cid,
            email='e',
            min_days=1,
            max_days=2,
            lookback_years=3,
            schedules_limit=100,
        )
        assert out == expected
        mock_service.get_inactive_clients.assert_awaited_once_with(
            cid,
            email='e',
            min_days=1,
            max_days=2,
            lookback_years=3,
            schedules_limit=100,
        )

    async def test_send_template_message(self, use_case, mock_service):
        cid = uuid4()
        await use_case.send_template_message(cid, '5511', 't')
        mock_service.send_template_message.assert_awaited_once_with(
            cid, '5511', override_text='t'
        )
